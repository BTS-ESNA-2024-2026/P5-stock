# ============================================================================
# SEED DATA
# ============================================================================

SEED_SQL = """

-- admin role
INSERT INTO role (id, name, "desc", perms)
VALUES (
    '019563a0-0000-7000-8000-000000000001',
    'admin',
    'system admins',
    '{"manage_admins": true, "admin_panel": true, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- technician role
INSERT INTO role (id, name, "desc", perms)
VALUES (
    '019563a0-0000-7000-8000-000000000002',
    'technician',
    'system technicien, like admin but cannot create other admins',
    '{"manage_admins": false, "admin_panel": true, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- secure_user role
INSERT INTO role (id, name, "desc", perms)
VALUES (
    '019563a0-0000-7000-8000-000000000003',
    'secure_user',
    'military user, RW on all assets',
    '{"manage_admins": false, "admin_panel": false, "sensible_access": true, "edit_assets": true, "view_assets": true}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- standard user role
INSERT INTO role (id, name, "desc", perms)
VALUES (
    '019563a0-0000-7000-8000-000000000004',
    'user',
    'standard military user, RW on most assets (non sensible)',
    '{"manage_admins": false, "admin_panel": false, "sensible_access": false, "edit_assets": true, "view_assets": true}'::jsonb
) ON CONFLICT (id) DO NOTHING;

-- viewer role
INSERT INTO role (id, name, "desc", perms)
VALUES (
    '019563a0-0000-7000-8000-000000000005',
    'viewer',
    'users for displays, read only',
    '{"manage_admins": false, "admin_panel": false, "sensible_access": false, "edit_assets": false, "view_assets": true}'::jsonb
) ON CONFLICT (id) DO NOTHING;

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
) ON CONFLICT (id) DO NOTHING;

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
) ON CONFLICT (id) DO NOTHING;

"""
