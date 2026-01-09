#!/bin/bash
# Script to configure replica to connect to primary
# This runs during container initialization

set -e

# Wait for MySQL to be ready
until mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "SELECT 1" &> /dev/null; do
    echo "Waiting for MySQL to be ready..."
    sleep 2
done

echo "MySQL is ready. Configuring replication..."

# Stop any existing replication
mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "STOP REPLICA;"

# Configure replication using GTID
mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} <<EOF
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='mysql-primary',
    SOURCE_PORT=3306,
    SOURCE_USER='replicator',
    SOURCE_PASSWORD='repl_password',
    SOURCE_AUTO_POSITION=1,
    GET_SOURCE_PUBLIC_KEY=1;

START REPLICA;
EOF

echo "Replication configured successfully!"

# Verify replication status
mysql -u root -p${MYSQL_ROOT_PASSWORD:-rootpassword} -e "SHOW REPLICA STATUS\G"
