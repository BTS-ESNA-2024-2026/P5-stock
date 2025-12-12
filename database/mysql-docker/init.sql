-- init to create table and main roles + system user
-- v1.3
CREATE TABLE IF NOT EXISTS `asset` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE COMMENT 'vehicle no 45, 12th HK 416...',
	`type_asset_id` TINYINT UNSIGNED NOT NULL,
	`mission_id` INTEGER COMMENT 'no assigned mission if value not assigned',
	`room_id` INTEGER,
	`DA` DATETIME NOT NULL,
	`DE` DATETIME NOT NULL,
	`name` TEXT NOT NULL COMMENT 'SN, PN, chassi no...',
	`number` TEXT COMMENT 'MRE number 3574
may not be necessary, depends',
	`status` ENUM('STOCK', 'DESTROYED', 'SOLD', 'LOST', 'TRANSIT', 'PURCHASED') NOT NULL,
	`quantity` INTEGER COMMENT 'for packs, do not set if quantity = 1 like for a vehicle',
	`shelf` TEXT(65535) COMMENT 'shelf no 355',
	`sensible` BOOLEAN,
	PRIMARY KEY(`id`)
) COMMENT='in mission, on repair, available...';


CREATE TABLE IF NOT EXISTS `asset_type` (
	`id` TINYINT UNSIGNED NOT NULL AUTO_INCREMENT UNIQUE COMMENT 'vehicle, MRE, weapon...',
	`type` TEXT NOT NULL COMMENT 'vehicle, MRE, weapon...',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `spec` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE COMMENT 'specs #7 = how much km a car has',
	`type_id` TINYINT UNSIGNED NOT NULL,
	`name` TEXT NOT NULL COMMENT 'km, expiration date, bullet...',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `value` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE COMMENT 'link between spec and asset by adding value : 3rd car''''s kilometers : 400000km',
	`asset_id` INTEGER NOT NULL,
	`spec_id` INTEGER NOT NULL,
	`DA` DATETIME NOT NULL,
	`DE` DATETIME NOT NULL,
	`value` TEXT NOT NULL COMMENT '25000Km, m855 ball point...',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `user` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`group_id` TINYINT NOT NULL,
	`DA` DATETIME NOT NULL,
	`DE` DATETIME NOT NULL,
	`active` BOOLEAN NOT NULL DEFAULT TRUE,
	`username` VARCHAR(255) NOT NULL UNIQUE,
	`name` TEXT,
	`hash` TEXT NOT NULL COMMENT '1945B09A02C889190B3',
	`hash_algorithm` TEXT NOT NULL COMMENT 'algo_rounds
ARGON2_32',
	`MFA` TEXT COMMENT 'seed of MFA',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `role` (
	`id` TINYINT NOT NULL AUTO_INCREMENT UNIQUE,
	`name` TEXT NOT NULL COMMENT 'admin, user',
	`desc` TEXT,
	`perms` BOOLEAN NOT NULL,
	PRIMARY KEY(`id`)
) COMMENT='admin, user, viewer, technician';


CREATE TABLE IF NOT EXISTS `log_admin` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`admin_id` INTEGER NOT NULL COMMENT 'required as first admin is created outside of the app so no dependency issue',
	`user_id` INTEGER NOT NULL,
	`D` DATETIME NOT NULL,
	`action` ENUM('CREATED', 'DELETED', 'EDITED', 'DEACTIVATED', 'ACTIVATED') NOT NULL COMMENT 'renamed john to martha',
	`desc` TEXT,
	PRIMARY KEY(`id`)
) COMMENT='separated admin logs for added security, when user (user_id) are edited/added... or when app settings are changed';


CREATE TABLE IF NOT EXISTS `log` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`asset_id` INTEGER NOT NULL,
	`spec_id` INTEGER,
	`value_id` INTEGER,
	`D` DATETIME NOT NULL,
	`action` ENUM('CREATED', 'DELETED', 'EDITED') NOT NULL COMMENT 'added car #3
changed bullet 7''''s grammage value',
	`description` TEXT(65535) COMMENT 'added helicopter 7''s kilometers',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `mission` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`DA` DATETIME NOT NULL,
	`DE` DATETIME NOT NULL,
	`date_start` DATETIME,
	`date_end` DATETIME,
	`title` TEXT(65535) NOT NULL,
	`description` TEXT(65535),
	`status` TEXT(65535) NOT NULL COMMENT 'finished, planned...',
	`theatre` TEXT(65535) NOT NULL COMMENT 'location',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `log_mission` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`mission_id` INTEGER NOT NULL,
	`D` DATETIME NOT NULL,
	`action` ENUM('CREATED', 'DELETED', 'EDITED') NOT NULL COMMENT 'changed date, removed description of mission...',
	`description` TEXT(65535) COMMENT '"changed value x from z to y"',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `room` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`base_id` INTEGER NOT NULL,
	`room` TEXT(65535) NOT NULL COMMENT 'Paris',
	PRIMARY KEY(`id`)
);


CREATE TABLE IF NOT EXISTS `base` (
	`id` INTEGER NOT NULL AUTO_INCREMENT UNIQUE,
	`name` TEXT(65535) NOT NULL,
	`address` TEXT(65535) NOT NULL,
	PRIMARY KEY(`id`)
);


ALTER TABLE `asset`
ADD FOREIGN KEY(`type_asset_id`) REFERENCES `asset_type`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `value`
ADD FOREIGN KEY(`asset_id`) REFERENCES `asset`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log_admin`
ADD FOREIGN KEY(`admin_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log`
ADD FOREIGN KEY(`asset_id`) REFERENCES `asset`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log_mission`
ADD FOREIGN KEY(`mission_id`) REFERENCES `mission`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `asset`
ADD FOREIGN KEY(`mission_id`) REFERENCES `mission`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log`
ADD FOREIGN KEY(`spec_id`) REFERENCES `spec`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log_admin`
ADD FOREIGN KEY(`user_id`) REFERENCES `user`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `room`
ADD FOREIGN KEY(`base_id`) REFERENCES `base`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `asset`
ADD FOREIGN KEY(`room_id`) REFERENCES `room`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `user`
ADD FOREIGN KEY(`group_id`) REFERENCES `role`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `spec`
ADD FOREIGN KEY(`type_id`) REFERENCES `asset_type`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `value`
ADD FOREIGN KEY(`spec_id`) REFERENCES `spec`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;
ALTER TABLE `log`
ADD FOREIGN KEY(`value_id`) REFERENCES `value`(`id`)
ON UPDATE NO ACTION ON DELETE NO ACTION;

-- admin role
INSERT INTO `role` (`id`, `name`, `desc`, `perms`)
VALUES (
  1,
  'admin',
  'system admins',
  JSON_OBJECT("manage_admins", true,
    "admin_panel", true,
    "sensible_access", true,
    "edit_assets", true,
    "view_assets", true)
);

-- technician role
INSERT INTO `role` (`id`, `name`, `desc`, `perms`)
VALUES (
  'technician',
  'system technicien, like admin but cannot create other admins',
  JSON_OBJECT("manage_admins", false,
    "admin_panel", true,
    "sensible_access", true,
    "edit_assets", true,
    "view_assets", true)
);

-- standard user role with sensible asset access
INSERT INTO `role` (`id`, `name`, `desc`, `perms`)
VALUES (
  'secure_user',
  'system admins',
  JSON_OBJECT("manage_admins", false,
    "admin_panel", false,
    "sensible_access", true,
    "edit_assets", true,
    "view_assets", true)
);

-- standard user role
INSERT INTO `role` (`id`, `name`, `desc`, `perms`)
VALUES (
  'user',
  'system admins',
  JSON_OBJECT("manage_admins", false,
    "admin_panel", false,
    "sensible_access", false,
    "edit_assets", true,
    "view_assets", true)
);

-- standard user role
INSERT INTO `role` (`id`, `name`, `desc`, `perms`)
VALUES (
  'user',
  'system admins',
  JSON_OBJECT("manage_admins", false,
    "admin_panel", false,
    "sensible_access", false,
    "edit_assets", false,
    "view_assets", true)
);

-- system user
INSERT INTO `user` (`group_id`, `DA`, `DE`, `active`, `username`, `name`, `hash`, `hash_algorithm`, `MFA`)
VALUES (
  1,
  NOW(),
  NOW(),
  TRUE,
  'system',
  'P5 main system user',
  '-',
  '-',
  NULL
);
