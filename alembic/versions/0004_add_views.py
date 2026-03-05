"""add database views

Revision ID: 0004
Revises: 0003
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


UPGRADE_SQL = """

-- Vue: Assets actifs avec informations détaillées
CREATE OR REPLACE VIEW view_active_assets AS
SELECT
    a.id,
    a.name,
    a.number,
    a.status,
    a.quantity,
    a.shelf,
    a.sensible,
    at.type AS asset_type,
    r.room AS room_name,
    b.name AS base_name,
    m.title AS mission_title,
    m.theatre AS mission_theatre,
    a."DA" AS created_at,
    a."DE" AS updated_at
FROM asset a
LEFT JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN room r ON a.room_id = r.id
LEFT JOIN base b ON r.base_id = b.id
LEFT JOIN mission m ON a.mission_id = m.id
WHERE a.status IN ('STOCK', 'TRANSIT', 'PURCHASED');

-- Vue: Assets en mission
CREATE OR REPLACE VIEW view_assets_in_mission AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    a.number,
    at.type AS asset_type,
    m.id AS mission_id,
    m.title AS mission_title,
    m.status AS mission_status,
    m.theatre,
    m.date_start,
    m.date_end
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
INNER JOIN mission m ON a.mission_id = m.id
WHERE a.mission_id IS NOT NULL;

-- Vue: Stock disponible par type
CREATE OR REPLACE VIEW view_stock_by_type AS
SELECT
    at.id AS type_id,
    at.type AS asset_type,
    COUNT(a.id) AS total_assets,
    SUM(COALESCE(a.quantity, 1)) AS total_quantity,
    SUM(CASE WHEN a.status = 'STOCK' THEN COALESCE(a.quantity, 1) ELSE 0 END) AS available_quantity
FROM asset_type at
LEFT JOIN asset a ON at.id = a.type_asset_id
GROUP BY at.id, at.type;

-- Vue: Missions actives avec comptage d'assets
CREATE OR REPLACE VIEW view_active_missions AS
SELECT
    m.id,
    m.title,
    m.status,
    m.theatre,
    m.date_start,
    m.date_end,
    COUNT(a.id) AS total_assets,
    m."DA" AS created_at,
    m."DE" AS updated_at
FROM mission m
LEFT JOIN asset a ON m.id = a.mission_id
WHERE m.status NOT IN ('finished', 'cancelled', 'archived')
GROUP BY m.id, m.title, m.status, m.theatre, m.date_start, m.date_end, m."DA", m."DE";

-- Vue: Historique complet des assets avec logs
CREATE OR REPLACE VIEW view_asset_history AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    at.type AS asset_type,
    l.id AS log_id,
    l."D" AS log_date,
    l.action AS log_action,
    l.description AS log_description
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN log l ON a.id = l.asset_id
ORDER BY a.id, l."D" DESC;

-- Vue: Valeurs actuelles des assets avec specs
CREATE OR REPLACE VIEW view_asset_values AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    at.type AS asset_type,
    s.name AS spec_name,
    v.value AS spec_value,
    v."DE" AS last_updated
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
INNER JOIN value v ON a.id = v.asset_id
INNER JOIN spec s ON v.spec_id = s.id
ORDER BY a.id, s.name;

-- Vue: Assets sensibles
CREATE OR REPLACE VIEW view_sensitive_assets AS
SELECT
    a.id,
    a.name,
    a.number,
    a.status,
    at.type AS asset_type,
    r.room AS room_name,
    b.name AS base_name,
    m.title AS mission_title
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN room r ON a.room_id = r.id
LEFT JOIN base b ON r.base_id = b.id
LEFT JOIN mission m ON a.mission_id = m.id
WHERE a.sensible = TRUE;

-- Vue: Utilisateurs actifs avec rôles
CREATE OR REPLACE VIEW view_active_users AS
SELECT
    u.id,
    u.username,
    u.name,
    u.active,
    r.name AS role_name,
    r."desc" AS role_description,
    u."MFA" AS has_mfa,
    u."DA" AS created_at,
    u."DE" AS updated_at
FROM "user" u
INNER JOIN role r ON u.group_id = r.id
WHERE u.active = TRUE;

-- Vue: Activité récente (tous les logs)
CREATE OR REPLACE VIEW view_recent_activity AS
SELECT
    'asset' AS log_type,
    l.id AS log_id,
    l."D" AS log_date,
    l.action::TEXT,
    l.description,
    a.name AS entity_name
FROM log l
LEFT JOIN asset a ON l.asset_id = a.id
UNION ALL
SELECT
    'admin' AS log_type,
    la.id AS log_id,
    la."D" AS log_date,
    la.action::TEXT,
    la."desc" AS description,
    u.username AS entity_name
FROM log_admin la
LEFT JOIN "user" u ON la.user_id = u.id
UNION ALL
SELECT
    'mission' AS log_type,
    lm.id AS log_id,
    lm."D" AS log_date,
    lm.action::TEXT,
    lm.description,
    m.title AS entity_name
FROM log_mission lm
LEFT JOIN mission m ON lm.mission_id = m.id
ORDER BY log_date DESC
LIMIT 100;

-- Vue: Stock par emplacement
CREATE OR REPLACE VIEW view_stock_by_location AS
SELECT
    b.id AS base_id,
    b.name AS base_name,
    r.id AS room_id,
    r.room AS room_name,
    at.type AS asset_type,
    COUNT(a.id) AS total_assets,
    SUM(COALESCE(a.quantity, 1)) AS total_quantity
FROM base b
INNER JOIN room r ON b.id = r.base_id
LEFT JOIN asset a ON r.id = a.room_id
LEFT JOIN asset_type at ON a.type_asset_id = at.id
WHERE a.status = 'STOCK'
GROUP BY b.id, b.name, r.id, r.room, at.type
ORDER BY b.name, r.room, at.type;

-- Vue: Assets avec toutes leurs spécifications
CREATE OR REPLACE VIEW view_complete_asset_info AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    a.number,
    a.status,
    a.quantity,
    a.shelf,
    a.sensible,
    at.type AS asset_type,
    r.room AS room_name,
    b.name AS base_name,
    b.address AS base_address,
    m.title AS mission_title,
    m.status AS mission_status,
    m.theatre AS mission_theatre,
    STRING_AGG(CONCAT(s.name, ': ', v.value), ' | ') AS specifications,
    a."DA" AS created_at,
    a."DE" AS updated_at
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN room r ON a.room_id = r.id
LEFT JOIN base b ON r.base_id = b.id
LEFT JOIN mission m ON a.mission_id = m.id
LEFT JOIN value v ON a.id = v.asset_id
LEFT JOIN spec s ON v.spec_id = s.id
GROUP BY a.id, a.name, a.number, a.status, a.quantity, a.shelf, a.sensible,
         at.type, r.room, b.name, b.address, m.title, m.status, m.theatre,
         a."DA", a."DE";

"""

DOWNGRADE_SQL = """
DROP VIEW IF EXISTS view_complete_asset_info;
DROP VIEW IF EXISTS view_stock_by_location;
DROP VIEW IF EXISTS view_recent_activity;
DROP VIEW IF EXISTS view_active_users;
DROP VIEW IF EXISTS view_sensitive_assets;
DROP VIEW IF EXISTS view_asset_values;
DROP VIEW IF EXISTS view_asset_history;
DROP VIEW IF EXISTS view_active_missions;
DROP VIEW IF EXISTS view_stock_by_type;
DROP VIEW IF EXISTS view_assets_in_mission;
DROP VIEW IF EXISTS view_active_assets;
"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(DOWNGRADE_SQL)
