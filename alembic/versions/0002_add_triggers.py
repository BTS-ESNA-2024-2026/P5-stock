"""add audit triggers and log protection

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-05

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '0002'
down_revision: Union[str, None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ============================================================================
# PL/pgSQL trigger functions + triggers
# ============================================================================

UPGRADE_SQL = """

-- ============================================================================
-- ASSET TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_after_asset_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, asset_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Asset created: ', NEW.name, ' (Type: ', NEW.type_asset_id, ', Status: ', NEW.status, ')')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_asset_insert
AFTER INSERT ON asset
FOR EACH ROW EXECUTE FUNCTION fn_after_asset_insert();


CREATE OR REPLACE FUNCTION fn_after_asset_update()
RETURNS TRIGGER AS $$
DECLARE
    changes TEXT := '';
BEGIN
    IF OLD.name IS DISTINCT FROM NEW.name THEN
        changes := changes || 'Name: "' || OLD.name || '" -> "' || NEW.name || '"; ';
    END IF;

    IF OLD.status IS DISTINCT FROM NEW.status THEN
        changes := changes || 'Status: "' || OLD.status || '" -> "' || NEW.status || '"; ';
    END IF;

    IF OLD.mission_id IS NULL AND NEW.mission_id IS NOT NULL THEN
        changes := changes || 'Mission assigned: ' || NEW.mission_id || '; ';
    ELSIF OLD.mission_id IS NOT NULL AND NEW.mission_id IS NULL THEN
        changes := changes || 'Mission removed: ' || OLD.mission_id || '; ';
    ELSIF OLD.mission_id IS DISTINCT FROM NEW.mission_id THEN
        changes := changes || 'Mission: ' || OLD.mission_id || ' -> ' || NEW.mission_id || '; ';
    END IF;

    IF OLD.room_id IS NULL AND NEW.room_id IS NOT NULL THEN
        changes := changes || 'Room assigned: ' || NEW.room_id || '; ';
    ELSIF OLD.room_id IS NOT NULL AND NEW.room_id IS NULL THEN
        changes := changes || 'Room removed: ' || OLD.room_id || '; ';
    ELSIF OLD.room_id IS DISTINCT FROM NEW.room_id THEN
        changes := changes || 'Room: ' || OLD.room_id || ' -> ' || NEW.room_id || '; ';
    END IF;

    IF COALESCE(OLD.quantity, 0) IS DISTINCT FROM COALESCE(NEW.quantity, 0) THEN
        changes := changes || 'Quantity: ' || COALESCE(OLD.quantity::TEXT, 'NULL') || ' -> ' || COALESCE(NEW.quantity::TEXT, 'NULL') || '; ';
    END IF;

    IF COALESCE(OLD.shelf, '') IS DISTINCT FROM COALESCE(NEW.shelf, '') THEN
        changes := changes || 'Shelf: "' || COALESCE(OLD.shelf, '') || '" -> "' || COALESCE(NEW.shelf, '') || '"; ';
    END IF;

    IF COALESCE(OLD.sensible, FALSE) IS DISTINCT FROM COALESCE(NEW.sensible, FALSE) THEN
        changes := changes || 'Sensible: ' || COALESCE(OLD.sensible::TEXT, 'false') || ' -> ' || COALESCE(NEW.sensible::TEXT, 'false') || '; ';
    END IF;

    IF changes != '' THEN
        INSERT INTO log (id, asset_id, "D", action, description)
        VALUES (gen_random_uuid(), NEW.id, NOW(), 'EDITED', changes);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_asset_update
AFTER UPDATE ON asset
FOR EACH ROW EXECUTE FUNCTION fn_after_asset_update();


CREATE OR REPLACE FUNCTION fn_after_asset_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, asset_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Asset deleted: ', OLD.name, ' (Type: ', OLD.type_asset_id, ', Status: ', OLD.status, ')')
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_asset_delete
AFTER DELETE ON asset
FOR EACH ROW EXECUTE FUNCTION fn_after_asset_delete();


-- ============================================================================
-- VALUE TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_after_value_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, asset_id, spec_id, value_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        NEW.asset_id,
        NEW.spec_id,
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Value created for asset ', NEW.asset_id, ', spec ', NEW.spec_id, ': "', NEW.value, '"')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_value_insert
AFTER INSERT ON value
FOR EACH ROW EXECUTE FUNCTION fn_after_value_insert();


CREATE OR REPLACE FUNCTION fn_after_value_update()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.value IS DISTINCT FROM NEW.value THEN
        INSERT INTO log (id, asset_id, spec_id, value_id, "D", action, description)
        VALUES (
            gen_random_uuid(),
            NEW.asset_id,
            NEW.spec_id,
            NEW.id,
            NOW(),
            'EDITED',
            CONCAT('Value updated for asset ', NEW.asset_id, ', spec ', NEW.spec_id, ': "', OLD.value, '" -> "', NEW.value, '"')
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_value_update
AFTER UPDATE ON value
FOR EACH ROW EXECUTE FUNCTION fn_after_value_update();


CREATE OR REPLACE FUNCTION fn_after_value_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, asset_id, spec_id, value_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        OLD.asset_id,
        OLD.spec_id,
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Value deleted for asset ', OLD.asset_id, ', spec ', OLD.spec_id, ': "', OLD.value, '"')
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_value_delete
AFTER DELETE ON value
FOR EACH ROW EXECUTE FUNCTION fn_after_value_delete();


-- ============================================================================
-- SPEC TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_after_spec_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, spec_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Spec created: ', NEW.name, ' (Type: ', NEW.type_id, ')')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_spec_insert
AFTER INSERT ON spec
FOR EACH ROW EXECUTE FUNCTION fn_after_spec_insert();


CREATE OR REPLACE FUNCTION fn_after_spec_update()
RETURNS TRIGGER AS $$
DECLARE
    changes TEXT := '';
BEGIN
    IF OLD.name IS DISTINCT FROM NEW.name THEN
        changes := changes || 'Name: "' || OLD.name || '" -> "' || NEW.name || '"; ';
    END IF;

    IF OLD.type_id IS DISTINCT FROM NEW.type_id THEN
        changes := changes || 'Type: ' || OLD.type_id || ' -> ' || NEW.type_id || '; ';
    END IF;

    IF changes != '' THEN
        INSERT INTO log (id, spec_id, "D", action, description)
        VALUES (gen_random_uuid(), NEW.id, NOW(), 'EDITED', changes);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_spec_update
AFTER UPDATE ON spec
FOR EACH ROW EXECUTE FUNCTION fn_after_spec_update();


CREATE OR REPLACE FUNCTION fn_after_spec_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log (id, spec_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Spec deleted: ', OLD.name, ' (Type: ', OLD.type_id, ')')
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_spec_delete
AFTER DELETE ON spec
FOR EACH ROW EXECUTE FUNCTION fn_after_spec_delete();


-- ============================================================================
-- USER TRIGGERS (LOG_ADMIN)
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_after_user_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_admin (id, user_id, "D", action, "desc")
    VALUES (
        gen_random_uuid(),
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('User created: ', NEW.username, ' (Group: ', NEW.group_id, ')')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_user_insert
AFTER INSERT ON "user"
FOR EACH ROW EXECUTE FUNCTION fn_after_user_insert();


CREATE OR REPLACE FUNCTION fn_after_user_update()
RETURNS TRIGGER AS $$
DECLARE
    changes TEXT := '';
    log_action log_admin_action;
BEGIN
    IF OLD.active = TRUE AND NEW.active = FALSE THEN
        log_action := 'DEACTIVATED';
        changes := CONCAT('User deactivated: ', NEW.username);
    ELSIF OLD.active = FALSE AND NEW.active = TRUE THEN
        log_action := 'ACTIVATED';
        changes := CONCAT('User activated: ', NEW.username);
    ELSE
        log_action := 'EDITED';

        IF OLD.username IS DISTINCT FROM NEW.username THEN
            changes := changes || 'Username: "' || OLD.username || '" -> "' || NEW.username || '"; ';
        END IF;

        IF COALESCE(OLD.name, '') IS DISTINCT FROM COALESCE(NEW.name, '') THEN
            changes := changes || 'Name: "' || COALESCE(OLD.name, '') || '" -> "' || COALESCE(NEW.name, '') || '"; ';
        END IF;

        IF OLD.group_id IS DISTINCT FROM NEW.group_id THEN
            changes := changes || 'Group: ' || OLD.group_id || ' -> ' || NEW.group_id || '; ';
        END IF;

        IF OLD.hash IS DISTINCT FROM NEW.hash THEN
            changes := changes || 'Password changed; ';
        END IF;

        IF COALESCE(OLD."MFA", '') IS DISTINCT FROM COALESCE(NEW."MFA", '') THEN
            IF NEW."MFA" IS NOT NULL AND NEW."MFA" != '' THEN
                changes := changes || 'MFA enabled; ';
            ELSE
                changes := changes || 'MFA disabled; ';
            END IF;
        END IF;
    END IF;

    IF changes != '' THEN
        INSERT INTO log_admin (id, user_id, "D", action, "desc")
        VALUES (gen_random_uuid(), NEW.id, NOW(), log_action, changes);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_user_update
AFTER UPDATE ON "user"
FOR EACH ROW EXECUTE FUNCTION fn_after_user_update();


CREATE OR REPLACE FUNCTION fn_after_user_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_admin (id, user_id, "D", action, "desc")
    VALUES (
        gen_random_uuid(),
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('User deleted: ', OLD.username, ' (Group: ', OLD.group_id, ')')
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_user_delete
AFTER DELETE ON "user"
FOR EACH ROW EXECUTE FUNCTION fn_after_user_delete();


-- ============================================================================
-- MISSION TRIGGERS (LOG_MISSION)
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_after_mission_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_mission (id, mission_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Mission created: ', NEW.title, ' (Theatre: ', NEW.theatre, ', Status: ', NEW.status, ')')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_mission_insert
AFTER INSERT ON mission
FOR EACH ROW EXECUTE FUNCTION fn_after_mission_insert();


CREATE OR REPLACE FUNCTION fn_after_mission_update()
RETURNS TRIGGER AS $$
DECLARE
    changes TEXT := '';
BEGIN
    IF OLD.title IS DISTINCT FROM NEW.title THEN
        changes := changes || 'Title: "' || OLD.title || '" -> "' || NEW.title || '"; ';
    END IF;

    IF COALESCE(OLD.description, '') IS DISTINCT FROM COALESCE(NEW.description, '') THEN
        changes := changes || 'Description changed; ';
    END IF;

    IF OLD.status IS DISTINCT FROM NEW.status THEN
        changes := changes || 'Status: "' || OLD.status || '" -> "' || NEW.status || '"; ';
    END IF;

    IF OLD.theatre IS DISTINCT FROM NEW.theatre THEN
        changes := changes || 'Theatre: "' || OLD.theatre || '" -> "' || NEW.theatre || '"; ';
    END IF;

    IF OLD.date_start IS NULL AND NEW.date_start IS NOT NULL THEN
        changes := changes || 'Start date set: ' || NEW.date_start || '; ';
    ELSIF OLD.date_start IS NOT NULL AND NEW.date_start IS NULL THEN
        changes := changes || 'Start date removed; ';
    ELSIF OLD.date_start IS DISTINCT FROM NEW.date_start THEN
        changes := changes || 'Start date: ' || OLD.date_start || ' -> ' || NEW.date_start || '; ';
    END IF;

    IF OLD.date_end IS NULL AND NEW.date_end IS NOT NULL THEN
        changes := changes || 'End date set: ' || NEW.date_end || '; ';
    ELSIF OLD.date_end IS NOT NULL AND NEW.date_end IS NULL THEN
        changes := changes || 'End date removed; ';
    ELSIF OLD.date_end IS DISTINCT FROM NEW.date_end THEN
        changes := changes || 'End date: ' || OLD.date_end || ' -> ' || NEW.date_end || '; ';
    END IF;

    IF changes != '' THEN
        INSERT INTO log_mission (id, mission_id, "D", action, description)
        VALUES (gen_random_uuid(), NEW.id, NOW(), 'EDITED', changes);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_mission_update
AFTER UPDATE ON mission
FOR EACH ROW EXECUTE FUNCTION fn_after_mission_update();


CREATE OR REPLACE FUNCTION fn_after_mission_delete()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO log_mission (id, mission_id, "D", action, description)
    VALUES (
        gen_random_uuid(),
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Mission deleted: ', OLD.title, ' (Theatre: ', OLD.theatre, ', Status: ', OLD.status, ')')
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_mission_delete
AFTER DELETE ON mission
FOR EACH ROW EXECUTE FUNCTION fn_after_mission_delete();


-- ============================================================================
-- LOG PROTECTION TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION fn_prevent_log_modify()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Interdit: les logs ne peuvent pas etre modifies ou supprimes';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_log_delete
BEFORE DELETE ON log
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

CREATE TRIGGER prevent_log_update
BEFORE UPDATE ON log
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

CREATE TRIGGER prevent_log_admin_delete
BEFORE DELETE ON log_admin
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

CREATE TRIGGER prevent_log_admin_update
BEFORE UPDATE ON log_admin
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

CREATE TRIGGER prevent_log_mission_delete
BEFORE DELETE ON log_mission
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

CREATE TRIGGER prevent_log_mission_update
BEFORE UPDATE ON log_mission
FOR EACH ROW EXECUTE FUNCTION fn_prevent_log_modify();

"""

DOWNGRADE_SQL = """
-- Drop all triggers
DROP TRIGGER IF EXISTS after_asset_insert ON asset;
DROP TRIGGER IF EXISTS after_asset_update ON asset;
DROP TRIGGER IF EXISTS after_asset_delete ON asset;
DROP TRIGGER IF EXISTS after_value_insert ON value;
DROP TRIGGER IF EXISTS after_value_update ON value;
DROP TRIGGER IF EXISTS after_value_delete ON value;
DROP TRIGGER IF EXISTS after_spec_insert ON spec;
DROP TRIGGER IF EXISTS after_spec_update ON spec;
DROP TRIGGER IF EXISTS after_spec_delete ON spec;
DROP TRIGGER IF EXISTS after_user_insert ON "user";
DROP TRIGGER IF EXISTS after_user_update ON "user";
DROP TRIGGER IF EXISTS after_user_delete ON "user";
DROP TRIGGER IF EXISTS after_mission_insert ON mission;
DROP TRIGGER IF EXISTS after_mission_update ON mission;
DROP TRIGGER IF EXISTS after_mission_delete ON mission;
DROP TRIGGER IF EXISTS prevent_log_delete ON log;
DROP TRIGGER IF EXISTS prevent_log_update ON log;
DROP TRIGGER IF EXISTS prevent_log_admin_delete ON log_admin;
DROP TRIGGER IF EXISTS prevent_log_admin_update ON log_admin;
DROP TRIGGER IF EXISTS prevent_log_mission_delete ON log_mission;
DROP TRIGGER IF EXISTS prevent_log_mission_update ON log_mission;

-- Drop all trigger functions
DROP FUNCTION IF EXISTS fn_after_asset_insert();
DROP FUNCTION IF EXISTS fn_after_asset_update();
DROP FUNCTION IF EXISTS fn_after_asset_delete();
DROP FUNCTION IF EXISTS fn_after_value_insert();
DROP FUNCTION IF EXISTS fn_after_value_update();
DROP FUNCTION IF EXISTS fn_after_value_delete();
DROP FUNCTION IF EXISTS fn_after_spec_insert();
DROP FUNCTION IF EXISTS fn_after_spec_update();
DROP FUNCTION IF EXISTS fn_after_spec_delete();
DROP FUNCTION IF EXISTS fn_after_user_insert();
DROP FUNCTION IF EXISTS fn_after_user_update();
DROP FUNCTION IF EXISTS fn_after_user_delete();
DROP FUNCTION IF EXISTS fn_after_mission_insert();
DROP FUNCTION IF EXISTS fn_after_mission_update();
DROP FUNCTION IF EXISTS fn_after_mission_delete();
DROP FUNCTION IF EXISTS fn_prevent_log_modify();
"""


def upgrade() -> None:
    op.execute(UPGRADE_SQL)


def downgrade() -> None:
    op.execute(DOWNGRADE_SQL)
