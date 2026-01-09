-- Setup replication user on Primary
-- This script runs on the primary server during initialization

-- Create replication user
CREATE USER IF NOT EXISTS 'replicator'@'%' IDENTIFIED BY 'repl_password';
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'replicator'@'%';

-- Create orchestrator user for topology discovery
CREATE USER IF NOT EXISTS 'orchestrator'@'%' IDENTIFIED BY 'orch_password';
GRANT SUPER, PROCESS, REPLICATION SLAVE, REPLICATION CLIENT, RELOAD ON *.* TO 'orchestrator'@'%';
GRANT SELECT ON mysql.slave_master_info TO 'orchestrator'@'%';
GRANT SELECT ON performance_schema.replication_group_members TO 'orchestrator'@'%';

-- Create ProxySQL monitor user
CREATE USER IF NOT EXISTS 'monitor'@'%' IDENTIFIED BY 'monitor';
GRANT REPLICATION CLIENT ON *.* TO 'monitor'@'%';
GRANT PROCESS ON *.* TO 'monitor'@'%';
GRANT SELECT ON sys.* TO 'monitor'@'%';

-- Create application user with limited privileges
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON P5DB.* TO 'app_user'@'%';

-- Create backup user
CREATE USER IF NOT EXISTS 'backup_user'@'%' IDENTIFIED BY 'backup_password';
GRANT SELECT, LOCK TABLES, SHOW VIEW, EVENT, TRIGGER, RELOAD ON *.* TO 'backup_user'@'%';

-- Create orchestrator database
CREATE DATABASE IF NOT EXISTS orchestrator;
GRANT ALL PRIVILEGES ON orchestrator.* TO 'orchestrator'@'%';

FLUSH PRIVILEGES;
