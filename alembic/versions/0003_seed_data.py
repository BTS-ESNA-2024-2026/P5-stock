"""seed default roles and system users

Revision ID: 0003
Revises: 0002
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Note: user insert triggers will auto-create log_admin entries.
    # Log protection triggers block DELETE/UPDATE on log tables,
    # so downgrade disables them temporarily.

    op.execute("""
        -- admin role
        INSERT INTO role (id, name, "desc", perms)
        VALUES (
            '019563a0-0000-7000-8000-000000000001',
            'admin',
            'system admins',
            '{"manage_admins": true, "admin_panel": true, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
        );

        -- technician role
        INSERT INTO role (id, name, "desc", perms)
        VALUES (
            '019563a0-0000-7000-8000-000000000002',
            'technician',
            'system technicien, like admin but cannot create other admins',
            '{"manage_admins": false, "admin_panel": true, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
        );

        -- secure_user role
        INSERT INTO role (id, name, "desc", perms)
        VALUES (
            '019563a0-0000-7000-8000-000000000003',
            'secure_user',
            'military user, RW on all assets',
            '{"manage_admins": false, "admin_panel": false, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
        );

        -- standard user role
        INSERT INTO role (id, name, "desc", perms)
        VALUES (
            '019563a0-0000-7000-8000-000000000004',
            'user',
            'standard military user, RW on most assets (non sensible)',
            '{"manage_admins": false, "admin_panel": false, "sensible_access": false, "edit_assets": true, "view_assets": true}'::jsonb
        );

        -- viewer role
        INSERT INTO role (id, name, "desc", perms)
        VALUES (
            '019563a0-0000-7000-8000-000000000005',
            'viewer',
            'users for displays, read only',
            '{"manage_admins": false, "admin_panel": false, "sensible_access": false, "edit_assets": false, "view_assets": true}'::jsonb
        );

        -- system user (admin role)
        INSERT INTO "user" (id, group_id, "DA", "DE", active, username, name, hash, hash_algorithm, "MFA")
        VALUES (
            '019563a0-0000-7000-8000-000000000010',
            '019563a0-0000-7000-8000-000000000001',
            NOW(),
            NOW(),
            TRUE,
            'system',
            'P5 main system user',
            '-',
            '-',
            NULL
        );

        -- default admin user
        INSERT INTO "user" (id, group_id, "DA", "DE", active, username, name, hash, hash_algorithm, "MFA")
        VALUES (
            '019563a0-0000-7000-8000-000000000011',
            '019563a0-0000-7000-8000-000000000001',
            NOW(),
            NOW(),
            TRUE,
            'defadm',
            'default admin',
            '$argon2id$v=19$m=65536,t=3,p=4$nLDw1TlJlTp2XlP3KZZjxQ$kpNEHHi5VRLsRD3eqIu+uFobDa1qWUIWgMx8RZ1bnwU',
            'argon2',
            NULL
        );
    """)


def downgrade() -> None:
    # Must temporarily disable log protection triggers to delete log_admin entries
    # created by the user insert triggers
    op.execute("""
        -- Disable log protection triggers
        ALTER TABLE log_admin DISABLE TRIGGER prevent_log_admin_delete;

        -- Delete log_admin entries for seed users
        DELETE FROM log_admin WHERE user_id IN (
            '019563a0-0000-7000-8000-000000000010',
            '019563a0-0000-7000-8000-000000000011'
        );

        -- Re-enable log protection triggers
        ALTER TABLE log_admin ENABLE TRIGGER prevent_log_admin_delete;

        -- Delete seed users
        DELETE FROM "user" WHERE id IN (
            '019563a0-0000-7000-8000-000000000010',
            '019563a0-0000-7000-8000-000000000011'
        );

        -- Delete seed roles
        DELETE FROM role WHERE id IN (
            '019563a0-0000-7000-8000-000000000001',
            '019563a0-0000-7000-8000-000000000002',
            '019563a0-0000-7000-8000-000000000003',
            '019563a0-0000-7000-8000-000000000004',
            '019563a0-0000-7000-8000-000000000005'
        );
    """)
