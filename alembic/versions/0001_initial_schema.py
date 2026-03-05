"""initial schema with uuid7 pks

Revision ID: 0001
Revises:
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -- role
    op.create_table(
        'role',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False, comment='admin, user'),
        sa.Column('desc', sa.Text(), nullable=True),
        sa.Column('perms', sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        comment='admin, user, viewer, technician',
    )

    # -- user
    op.create_table(
        'user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('group_id', sa.Uuid(), nullable=False),
        sa.Column('DA', sa.DateTime(), nullable=False),
        sa.Column('DE', sa.DateTime(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.Column('hash', sa.Text(), nullable=False, comment='1945B09A02C889190B3'),
        sa.Column('hash_algorithm', sa.Text(), nullable=False, comment='algo_rounds\nARGON2_32'),
        sa.Column('MFA', sa.Text(), nullable=True, comment='seed of MFA'),
        sa.ForeignKeyConstraint(['group_id'], ['role.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
    )

    # -- base
    op.create_table(
        'base',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('address', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- room
    op.create_table(
        'room',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('base_id', sa.Uuid(), nullable=False),
        sa.Column('room', sa.Text(), nullable=False, comment='Paris'),
        sa.ForeignKeyConstraint(['base_id'], ['base.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- asset_type
    op.create_table(
        'asset_type',
        sa.Column('id', sa.Uuid(), nullable=False, comment='vehicle, MRE, weapon...'),
        sa.Column('type', sa.Text(), nullable=False, comment='vehicle, MRE, weapon...'),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- mission
    op.create_table(
        'mission',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('DA', sa.DateTime(), nullable=False),
        sa.Column('DE', sa.DateTime(), nullable=False),
        sa.Column('date_start', sa.DateTime(), nullable=True),
        sa.Column('date_end', sa.DateTime(), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Text(), nullable=False, comment='finished, planned...'),
        sa.Column('theatre', sa.Text(), nullable=False, comment='location'),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- asset (depends on asset_type, mission, room)
    asset_status = sa.Enum('STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED', name='asset_status')
    op.create_table(
        'asset',
        sa.Column('id', sa.Uuid(), nullable=False, comment='vehicle no 45, 12th HK 416...'),
        sa.Column('type_asset_id', sa.Uuid(), nullable=False),
        sa.Column('mission_id', sa.Uuid(), nullable=True, comment='no assigned mission if value not assigned'),
        sa.Column('room_id', sa.Uuid(), nullable=True),
        sa.Column('DA', sa.DateTime(), nullable=False),
        sa.Column('DE', sa.DateTime(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False, comment='SN, PN, chassi no...'),
        sa.Column('number', sa.Text(), nullable=True, comment='MRE number 3574\nmay not be necessary, depends'),
        sa.Column('status', asset_status, nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=True, comment='for packs, do not set if quantity = 1 like for a vehicle'),
        sa.Column('shelf', sa.Text(), nullable=True, comment='shelf no 355'),
        sa.Column('sensible', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['type_asset_id'], ['asset_type.id']),
        sa.ForeignKeyConstraint(['mission_id'], ['mission.id']),
        sa.ForeignKeyConstraint(['room_id'], ['room.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='in mission, on repair, available...',
    )

    # -- spec
    op.create_table(
        'spec',
        sa.Column('id', sa.Uuid(), nullable=False, comment='specs #7 = how much km a car has'),
        sa.Column('type_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False, comment='km, expiration date, bullet...'),
        sa.ForeignKeyConstraint(['type_id'], ['asset_type.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- value
    op.create_table(
        'value',
        sa.Column('id', sa.Uuid(), nullable=False, comment="link between spec and asset by adding value"),
        sa.Column('asset_id', sa.Uuid(), nullable=False),
        sa.Column('spec_id', sa.Uuid(), nullable=False),
        sa.Column('DA', sa.DateTime(), nullable=False),
        sa.Column('DE', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False, comment='25000Km, m855 ball point...'),
        sa.ForeignKeyConstraint(['asset_id'], ['asset.id']),
        sa.ForeignKeyConstraint(['spec_id'], ['spec.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- log_admin
    log_admin_action = sa.Enum('CREATED', 'DELETED', 'EDITED', 'DEACTIVATED', 'ACTIVATED', name='log_admin_action')
    op.create_table(
        'log_admin',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('D', sa.DateTime(), nullable=False),
        sa.Column('action', log_admin_action, nullable=False, comment='renamed john to martha'),
        sa.Column('desc', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
        comment='separated admin logs for added security',
    )

    # -- log
    log_action = sa.Enum('CREATED', 'DELETED', 'EDITED', name='log_action')
    op.create_table(
        'log',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('asset_id', sa.Uuid(), nullable=True),
        sa.Column('spec_id', sa.Uuid(), nullable=True),
        sa.Column('value_id', sa.Uuid(), nullable=True),
        sa.Column('D', sa.DateTime(), nullable=False),
        sa.Column('action', log_action, nullable=False, comment='added car #3'),
        sa.Column('description', sa.Text(), nullable=True, comment="added helicopter 7's kilometers"),
        sa.ForeignKeyConstraint(['asset_id'], ['asset.id']),
        sa.ForeignKeyConstraint(['spec_id'], ['spec.id']),
        sa.ForeignKeyConstraint(['value_id'], ['value.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # -- log_mission
    log_mission_action = sa.Enum('CREATED', 'DELETED', 'EDITED', name='log_mission_action')
    op.create_table(
        'log_mission',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('mission_id', sa.Uuid(), nullable=False),
        sa.Column('D', sa.DateTime(), nullable=False),
        sa.Column('action', log_mission_action, nullable=False, comment='changed date, removed description of mission...'),
        sa.Column('description', sa.Text(), nullable=True, comment='"changed value x from z to y"'),
        sa.ForeignKeyConstraint(['mission_id'], ['mission.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('log_mission')
    op.drop_table('log')
    op.drop_table('log_admin')
    op.drop_table('value')
    op.drop_table('spec')
    op.drop_table('asset')
    op.drop_table('mission')
    op.drop_table('asset_type')
    op.drop_table('room')
    op.drop_table('base')
    op.drop_table('user')
    op.drop_table('role')
    sa.Enum(name='asset_status').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='log_admin_action').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='log_action').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='log_mission_action').drop(op.get_bind(), checkfirst=True)
