-- ============================================================================
-- TRIGGERS POUR LA GESTION AUTOMATIQUE DES LOGS
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TRIGGERS POUR LA TABLE ASSET
-- ----------------------------------------------------------------------------

DELIMITER $$

-- Trigger après insertion d'un asset
CREATE TRIGGER after_asset_insert
AFTER INSERT ON `asset`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`asset_id`, `D`, `action`, `description`)
    VALUES (
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Asset created: ', NEW.name, ' (Type: ', NEW.type_asset_id, ', Status: ', NEW.status, ')')
    );
END$$

-- Trigger après mise à jour d'un asset
CREATE TRIGGER after_asset_update
AFTER UPDATE ON `asset`
FOR EACH ROW
BEGIN
    DECLARE changes TEXT DEFAULT '';

    IF OLD.name != NEW.name THEN
        SET changes = CONCAT(changes, 'Name: "', OLD.name, '" -> "', NEW.name, '"; ');
    END IF;

    IF OLD.status != NEW.status THEN
        SET changes = CONCAT(changes, 'Status: "', OLD.status, '" -> "', NEW.status, '"; ');
    END IF;

    IF OLD.mission_id IS NULL AND NEW.mission_id IS NOT NULL THEN
        SET changes = CONCAT(changes, 'Mission assigned: ', NEW.mission_id, '; ');
    ELSEIF OLD.mission_id IS NOT NULL AND NEW.mission_id IS NULL THEN
        SET changes = CONCAT(changes, 'Mission removed: ', OLD.mission_id, '; ');
    ELSEIF OLD.mission_id != NEW.mission_id THEN
        SET changes = CONCAT(changes, 'Mission: ', OLD.mission_id, ' -> ', NEW.mission_id, '; ');
    END IF;

    IF OLD.room_id IS NULL AND NEW.room_id IS NOT NULL THEN
        SET changes = CONCAT(changes, 'Room assigned: ', NEW.room_id, '; ');
    ELSEIF OLD.room_id IS NOT NULL AND NEW.room_id IS NULL THEN
        SET changes = CONCAT(changes, 'Room removed: ', OLD.room_id, '; ');
    ELSEIF OLD.room_id != NEW.room_id THEN
        SET changes = CONCAT(changes, 'Room: ', OLD.room_id, ' -> ', NEW.room_id, '; ');
    END IF;

    IF IFNULL(OLD.quantity, 0) != IFNULL(NEW.quantity, 0) THEN
        SET changes = CONCAT(changes, 'Quantity: ', IFNULL(OLD.quantity, 'NULL'), ' -> ', IFNULL(NEW.quantity, 'NULL'), '; ');
    END IF;

    IF IFNULL(OLD.shelf, '') != IFNULL(NEW.shelf, '') THEN
        SET changes = CONCAT(changes, 'Shelf: "', IFNULL(OLD.shelf, ''), '" -> "', IFNULL(NEW.shelf, ''), '"; ');
    END IF;

    IF IFNULL(OLD.sensible, 0) != IFNULL(NEW.sensible, 0) THEN
        SET changes = CONCAT(changes, 'Sensible: ', IFNULL(OLD.sensible, 0), ' -> ', IFNULL(NEW.sensible, 0), '; ');
    END IF;

    IF changes != '' THEN
        INSERT INTO `log` (`asset_id`, `D`, `action`, `description`)
        VALUES (NEW.id, NOW(), 'EDITED', changes);
    END IF;
END$$

-- Trigger après suppression d'un asset
CREATE TRIGGER after_asset_delete
AFTER DELETE ON `asset`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`asset_id`, `D`, `action`, `description`)
    VALUES (
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Asset deleted: ', OLD.name, ' (Type: ', OLD.type_asset_id, ', Status: ', OLD.status, ')')
    );
END$$

-- ----------------------------------------------------------------------------
-- TRIGGERS POUR LA TABLE VALUE
-- ----------------------------------------------------------------------------

-- Trigger après insertion d'une value
CREATE TRIGGER after_value_insert
AFTER INSERT ON `value`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`asset_id`, `spec_id`, `value_id`, `D`, `action`, `description`)
    VALUES (
        NEW.asset_id,
        NEW.spec_id,
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Value created for asset ', NEW.asset_id, ', spec ', NEW.spec_id, ': "', NEW.value, '"')
    );
END$$

-- Trigger après mise à jour d'une value
CREATE TRIGGER after_value_update
AFTER UPDATE ON `value`
FOR EACH ROW
BEGIN
    IF OLD.value != NEW.value THEN
        INSERT INTO `log` (`asset_id`, `spec_id`, `value_id`, `D`, `action`, `description`)
        VALUES (
            NEW.asset_id,
            NEW.spec_id,
            NEW.id,
            NOW(),
            'EDITED',
            CONCAT('Value updated for asset ', NEW.asset_id, ', spec ', NEW.spec_id, ': "', OLD.value, '" -> "', NEW.value, '"')
        );
    END IF;
END$$

-- Trigger après suppression d'une value
CREATE TRIGGER after_value_delete
AFTER DELETE ON `value`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`asset_id`, `spec_id`, `value_id`, `D`, `action`, `description`)
    VALUES (
        OLD.asset_id,
        OLD.spec_id,
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Value deleted for asset ', OLD.asset_id, ', spec ', OLD.spec_id, ': "', OLD.value, '"')
    );
END$$

-- ----------------------------------------------------------------------------
-- TRIGGERS POUR LA TABLE SPEC
-- ----------------------------------------------------------------------------

-- Trigger après insertion d'un spec
CREATE TRIGGER after_spec_insert
AFTER INSERT ON `spec`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`spec_id`, `D`, `action`, `description`)
    VALUES (
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Spec created: ', NEW.name, ' (Type: ', NEW.type_id, ')')
    );
END$$

-- Trigger après mise à jour d'un spec
CREATE TRIGGER after_spec_update
AFTER UPDATE ON `spec`
FOR EACH ROW
BEGIN
    DECLARE changes TEXT DEFAULT '';

    IF OLD.name != NEW.name THEN
        SET changes = CONCAT(changes, 'Name: "', OLD.name, '" -> "', NEW.name, '"; ');
    END IF;

    IF OLD.type_id != NEW.type_id THEN
        SET changes = CONCAT(changes, 'Type: ', OLD.type_id, ' -> ', NEW.type_id, '; ');
    END IF;

    IF changes != '' THEN
        INSERT INTO `log` (`spec_id`, `D`, `action`, `description`)
        VALUES (NEW.id, NOW(), 'EDITED', changes);
    END IF;
END$$

-- Trigger après suppression d'un spec
CREATE TRIGGER after_spec_delete
AFTER DELETE ON `spec`
FOR EACH ROW
BEGIN
    INSERT INTO `log` (`spec_id`, `D`, `action`, `description`)
    VALUES (
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Spec deleted: ', OLD.name, ' (Type: ', OLD.type_id, ')')
    );
END$$

-- ----------------------------------------------------------------------------
-- TRIGGERS POUR LA TABLE USER (LOG_ADMIN)
-- ----------------------------------------------------------------------------

-- Trigger après insertion d'un user
CREATE TRIGGER after_user_insert
AFTER INSERT ON `user`
FOR EACH ROW
BEGIN
    INSERT INTO `log_admin` (`user_id`, `D`, `action`, `desc`)
    VALUES (
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('User created: ', NEW.username, ' (Group: ', NEW.group_id, ')')
    );
END$$

-- Trigger après mise à jour d'un user
CREATE TRIGGER after_user_update
AFTER UPDATE ON `user`
FOR EACH ROW
BEGIN
    DECLARE changes TEXT DEFAULT '';
    DECLARE log_action ENUM('CREATED', 'DELETED', 'EDITED', 'DEACTIVATED', 'ACTIVATED');

    IF OLD.active = TRUE AND NEW.active = FALSE THEN
        SET log_action = 'DEACTIVATED';
        SET changes = CONCAT('User deactivated: ', NEW.username);
    ELSEIF OLD.active = FALSE AND NEW.active = TRUE THEN
        SET log_action = 'ACTIVATED';
        SET changes = CONCAT('User activated: ', NEW.username);
    ELSE
        SET log_action = 'EDITED';

        IF OLD.username != NEW.username THEN
            SET changes = CONCAT(changes, 'Username: "', OLD.username, '" -> "', NEW.username, '"; ');
        END IF;

        IF IFNULL(OLD.name, '') != IFNULL(NEW.name, '') THEN
            SET changes = CONCAT(changes, 'Name: "', IFNULL(OLD.name, ''), '" -> "', IFNULL(NEW.name, ''), '"; ');
        END IF;

        IF OLD.group_id != NEW.group_id THEN
            SET changes = CONCAT(changes, 'Group: ', OLD.group_id, ' -> ', NEW.group_id, '; ');
        END IF;

        IF OLD.hash != NEW.hash THEN
            SET changes = CONCAT(changes, 'Password changed; ');
        END IF;

        IF IFNULL(OLD.MFA, '') != IFNULL(NEW.MFA, '') THEN
            IF NEW.MFA IS NOT NULL AND NEW.MFA != '' THEN
                SET changes = CONCAT(changes, 'MFA enabled; ');
            ELSE
                SET changes = CONCAT(changes, 'MFA disabled; ');
            END IF;
        END IF;
    END IF;

    IF changes != '' THEN
        INSERT INTO `log_admin` (`user_id`, `D`, `action`, `desc`)
        VALUES (NEW.id, NOW(), log_action, changes);
    END IF;
END$$

-- Trigger après suppression d'un user
CREATE TRIGGER after_user_delete
AFTER DELETE ON `user`
FOR EACH ROW
BEGIN
    INSERT INTO `log_admin` (`user_id`, `D`, `action`, `desc`)
    VALUES (
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('User deleted: ', OLD.username, ' (Group: ', OLD.group_id, ')')
    );
END$$

-- ----------------------------------------------------------------------------
-- TRIGGERS POUR LA TABLE MISSION (LOG_MISSION)
-- ----------------------------------------------------------------------------

-- Trigger après insertion d'une mission
CREATE TRIGGER after_mission_insert
AFTER INSERT ON `mission`
FOR EACH ROW
BEGIN
    INSERT INTO `log_mission` (`mission_id`, `D`, `action`, `description`)
    VALUES (
        NEW.id,
        NOW(),
        'CREATED',
        CONCAT('Mission created: ', NEW.title, ' (Theatre: ', NEW.theatre, ', Status: ', NEW.status, ')')
    );
END$$

-- Trigger après mise à jour d'une mission
CREATE TRIGGER after_mission_update
AFTER UPDATE ON `mission`
FOR EACH ROW
BEGIN
    DECLARE changes TEXT DEFAULT '';

    IF OLD.title != NEW.title THEN
        SET changes = CONCAT(changes, 'Title: "', OLD.title, '" -> "', NEW.title, '"; ');
    END IF;

    IF IFNULL(OLD.description, '') != IFNULL(NEW.description, '') THEN
        SET changes = CONCAT(changes, 'Description changed; ');
    END IF;

    IF OLD.status != NEW.status THEN
        SET changes = CONCAT(changes, 'Status: "', OLD.status, '" -> "', NEW.status, '"; ');
    END IF;

    IF OLD.theatre != NEW.theatre THEN
        SET changes = CONCAT(changes, 'Theatre: "', OLD.theatre, '" -> "', NEW.theatre, '"; ');
    END IF;

    IF OLD.date_start IS NULL AND NEW.date_start IS NOT NULL THEN
        SET changes = CONCAT(changes, 'Start date set: ', NEW.date_start, '; ');
    ELSEIF OLD.date_start IS NOT NULL AND NEW.date_start IS NULL THEN
        SET changes = CONCAT(changes, 'Start date removed; ');
    ELSEIF OLD.date_start != NEW.date_start THEN
        SET changes = CONCAT(changes, 'Start date: ', OLD.date_start, ' -> ', NEW.date_start, '; ');
    END IF;

    IF OLD.date_end IS NULL AND NEW.date_end IS NOT NULL THEN
        SET changes = CONCAT(changes, 'End date set: ', NEW.date_end, '; ');
    ELSEIF OLD.date_end IS NOT NULL AND NEW.date_end IS NULL THEN
        SET changes = CONCAT(changes, 'End date removed; ');
    ELSEIF OLD.date_end != NEW.date_end THEN
        SET changes = CONCAT(changes, 'End date: ', OLD.date_end, ' -> ', NEW.date_end, '; ');
    END IF;

    IF changes != '' THEN
        INSERT INTO `log_mission` (`mission_id`, `D`, `action`, `description`)
        VALUES (NEW.id, NOW(), 'EDITED', changes);
    END IF;
END$$

-- Trigger après suppression d'une mission
CREATE TRIGGER after_mission_delete
AFTER DELETE ON `mission`
FOR EACH ROW
BEGIN
    INSERT INTO `log_mission` (`mission_id`, `D`, `action`, `description`)
    VALUES (
        OLD.id,
        NOW(),
        'DELETED',
        CONCAT('Mission deleted: ', OLD.title, ' (Theatre: ', OLD.theatre, ', Status: ', OLD.status, ')')
    );
END$$

DELIMITER ;

-- ============================================================================
-- TRIGGERS DE PROTECTION CONTRE LA SUPPRESSION DES LOGS
-- ============================================================================

DELIMITER $$

-- Protection table LOG
CREATE TRIGGER prevent_log_delete
BEFORE DELETE ON `log`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Suppression interdite: Les logs ne peuvent pas être supprimés';
END$$

CREATE TRIGGER prevent_log_update
BEFORE UPDATE ON `log`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Modification interdite: Les logs ne peuvent pas être modifiés';
END$$

-- Protection table LOG_ADMIN
CREATE TRIGGER prevent_log_admin_delete
BEFORE DELETE ON `log_admin`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Suppression interdite: Les logs admin ne peuvent pas être supprimés';
END$$

CREATE TRIGGER prevent_log_admin_update
BEFORE UPDATE ON `log_admin`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Modification interdite: Les logs admin ne peuvent pas être modifiés';
END$$

-- Protection table LOG_MISSION
CREATE TRIGGER prevent_log_mission_delete
BEFORE DELETE ON `log_mission`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Suppression interdite: Les logs mission ne peuvent pas être supprimés';
END$$

CREATE TRIGGER prevent_log_mission_update
BEFORE UPDATE ON `log_mission`
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
    SET MESSAGE_TEXT = 'Modification interdite: Les logs mission ne peuvent pas être modifiés';
END$$

DELIMITER ;

-- ============================================================================
-- VUES UTILES POUR LE PROJET
-- ============================================================================

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
    a.DA AS created_at,
    a.DE AS updated_at
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
    SUM(IFNULL(a.quantity, 1)) AS total_quantity,
    SUM(CASE WHEN a.status = 'STOCK' THEN IFNULL(a.quantity, 1) ELSE 0 END) AS available_quantity
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
    m.DA AS created_at,
    m.DE AS updated_at
FROM mission m
LEFT JOIN asset a ON m.id = a.mission_id
WHERE m.status NOT IN ('finished', 'cancelled', 'archived')
GROUP BY m.id, m.title, m.status, m.theatre, m.date_start, m.date_end, m.DA, m.DE;

-- Vue: Historique complet des assets avec logs
CREATE OR REPLACE VIEW view_asset_history AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    at.type AS asset_type,
    l.id AS log_id,
    l.D AS log_date,
    l.action AS log_action,
    l.description AS log_description
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN log l ON a.id = l.asset_id
ORDER BY a.id, l.D DESC;

-- Vue: Valeurs actuelles des assets avec specs
CREATE OR REPLACE VIEW view_asset_values AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    at.type AS asset_type,
    s.name AS spec_name,
    v.value AS spec_value,
    v.DE AS last_updated
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
    r.desc AS role_description,
    u.MFA AS has_mfa,
    u.DA AS created_at,
    u.DE AS updated_at
FROM user u
INNER JOIN role r ON u.group_id = r.id
WHERE u.active = TRUE;

-- Vue: Activité récente (tous les logs)
CREATE OR REPLACE VIEW view_recent_activity AS
SELECT
    'asset' AS log_type,
    l.id AS log_id,
    l.D AS log_date,
    l.action,
    l.description,
    a.name AS entity_name
FROM log l
LEFT JOIN asset a ON l.asset_id = a.id
UNION ALL
SELECT
    'admin' AS log_type,
    la.id AS log_id,
    la.D AS log_date,
    la.action,
    la.desc AS description,
    u.username AS entity_name
FROM log_admin la
LEFT JOIN user u ON la.user_id = u.id
UNION ALL
SELECT
    'mission' AS log_type,
    lm.id AS log_id,
    lm.D AS log_date,
    lm.action,
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
    SUM(IFNULL(a.quantity, 1)) AS total_quantity
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
    GROUP_CONCAT(CONCAT(s.name, ': ', v.value) SEPARATOR ' | ') AS specifications,
    a.DA AS created_at,
    a.DE AS updated_at
FROM asset a
INNER JOIN asset_type at ON a.type_asset_id = at.id
LEFT JOIN room r ON a.room_id = r.id
LEFT JOIN base b ON r.base_id = b.id
LEFT JOIN mission m ON a.mission_id = m.id
LEFT JOIN value v ON a.id = v.asset_id
LEFT JOIN spec s ON v.spec_id = s.id
GROUP BY a.id, a.name, a.number, a.status, a.quantity, a.shelf, a.sensible,
         at.type, r.room, b.name, b.address, m.title, m.status, m.theatre,
         a.DA, a.DE;