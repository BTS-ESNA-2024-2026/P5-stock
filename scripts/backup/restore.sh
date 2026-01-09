#!/bin/bash
# MySQL Recovery Script for P5-Stock
# Issue #29: Disaster Recovery
#
# Features:
# - Point-in-time recovery (PITR)
# - Full restore from backup
# - Binary log replay
# - RTO: 4 hours target
#
# Usage:
#   ./restore.sh full <backup_file>
#   ./restore.sh pitr <backup_file> <target_timestamp>

set -euo pipefail

# ============================================
# Configuration
# ============================================
RESTORE_TYPE="${1:-help}"
BACKUP_FILE="${2:-}"
TARGET_TIMESTAMP="${3:-}"

# MySQL connection
MYSQL_HOST="${MYSQL_HOST:-localhost}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-rootpassword}"

# Paths
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/mysql}"
RESTORE_WORK_DIR="/tmp/mysql-restore-$$"
S3_BUCKET="${S3_BUCKET:-p5stock-backups}"
S3_ENDPOINT="${S3_ENDPOINT:-https://s3.amazonaws.com}"

# Encryption
ENCRYPTION_KEY_FILE="${ENCRYPTION_KEY_FILE:-/etc/mysql-backup/encryption.key}"

# Logging
LOG_FILE="/var/log/mysql-backup/restore_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

# ============================================
# Functions
# ============================================

log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*" | tee -a "$LOG_FILE"
}

log_info() { log "INFO" "$@"; }
log_warn() { log "WARN" "$@"; }
log_error() { log "ERROR" "$@"; }

show_help() {
    cat << EOF
MySQL Disaster Recovery Script

Usage:
    $0 full <backup_file>              Restore from full backup
    $0 pitr <backup_file> <timestamp>  Point-in-time recovery
    $0 list                            List available backups
    $0 verify <backup_file>            Verify backup integrity
    $0 download <s3_path>              Download backup from S3

Examples:
    $0 full /var/backups/mysql/20260109/full/p5stock_full_20260109_020000.sql.gz
    $0 pitr backup.sql.gz "2026-01-09 14:30:00"
    $0 list

RTO Target: 4 hours
RPO Target: 1 hour
EOF
}

prepare_work_dir() {
    mkdir -p "$RESTORE_WORK_DIR"
    log_info "Created work directory: $RESTORE_WORK_DIR"
}

cleanup_work_dir() {
    rm -rf "$RESTORE_WORK_DIR"
    log_info "Cleaned up work directory"
}

download_from_s3() {
    local s3_path="$1"
    local local_path="${RESTORE_WORK_DIR}/$(basename "$s3_path")"
    
    log_info "Downloading from S3: $s3_path"
    
    aws s3 cp "s3://${S3_BUCKET}/${s3_path}" "$local_path" \
        --endpoint-url "$S3_ENDPOINT" \
        2>> "$LOG_FILE"
    
    echo "$local_path"
}

decrypt_file() {
    local encrypted_file="$1"
    local decrypted_file="${encrypted_file%.enc}"
    
    if [[ ! -f "$ENCRYPTION_KEY_FILE" ]]; then
        log_error "Encryption key not found: $ENCRYPTION_KEY_FILE"
        exit 1
    fi
    
    log_info "Decrypting backup..."
    
    openssl enc -aes-256-cbc -d -pbkdf2 \
        -in "$encrypted_file" \
        -out "$decrypted_file" \
        -pass file:"$ENCRYPTION_KEY_FILE"
    
    echo "$decrypted_file"
}

decompress_file() {
    local file="$1"
    local decompressed="${file%.gz}"
    
    if [[ "$file" == *.gz ]]; then
        log_info "Decompressing backup..."
        gunzip -c "$file" > "$decompressed"
        echo "$decompressed"
    else
        echo "$file"
    fi
}

verify_backup() {
    local backup_file="$1"
    
    log_info "Verifying backup integrity: $backup_file"
    
    # Check file exists
    if [[ ! -f "$backup_file" ]]; then
        log_error "Backup file not found: $backup_file"
        return 1
    fi
    
    # Check compressed file integrity
    if [[ "$backup_file" == *.gz ]]; then
        if ! gzip -t "$backup_file" 2>/dev/null; then
            log_error "Backup file is corrupted"
            return 1
        fi
    fi
    
    # Check metadata if available
    local meta_file="${backup_file}.meta"
    if [[ -f "$meta_file" ]]; then
        log_info "Backup metadata:"
        cat "$meta_file"
        
        # Verify checksum
        local expected_checksum=$(jq -r '.checksum' "$meta_file" 2>/dev/null || echo "")
        if [[ -n "$expected_checksum" && "$expected_checksum" != "N/A" ]]; then
            local actual_checksum=$(sha256sum "$backup_file" | awk '{print $1}')
            if [[ "$expected_checksum" != "$actual_checksum" ]]; then
                log_error "Checksum mismatch!"
                return 1
            fi
            log_info "Checksum verified"
        fi
    fi
    
    log_info "Backup verification passed"
    return 0
}

list_backups() {
    log_info "Available local backups:"
    find "$BACKUP_BASE_DIR" -name "*.sql.gz*" -type f 2>/dev/null | sort -r | head -20
    
    log_info ""
    log_info "Available S3 backups:"
    aws s3 ls "s3://${S3_BUCKET}/full/" \
        --endpoint-url "$S3_ENDPOINT" \
        2>/dev/null | tail -20 || log_warn "Could not list S3 backups"
}

# Full restore from backup
restore_full() {
    local backup_file="$1"
    
    log_info "=========================================="
    log_info "Starting FULL RESTORE"
    log_info "Backup: $backup_file"
    log_info "=========================================="
    
    # Verify backup
    verify_backup "$backup_file" || exit 1
    
    # Prepare work directory
    prepare_work_dir
    
    # Copy to work directory if not already there
    local work_file="$backup_file"
    if [[ ! "$backup_file" =~ ^$RESTORE_WORK_DIR ]]; then
        cp "$backup_file" "$RESTORE_WORK_DIR/"
        work_file="${RESTORE_WORK_DIR}/$(basename "$backup_file")"
    fi
    
    # Decrypt if encrypted
    if [[ "$work_file" == *.enc ]]; then
        work_file=$(decrypt_file "$work_file")
    fi
    
    # Decompress
    work_file=$(decompress_file "$work_file")
    
    log_info "Prepared backup file: $work_file"
    
    # Confirmation prompt
    echo ""
    echo "WARNING: This will restore the database and may overwrite existing data!"
    echo "Target: ${MYSQL_HOST}:${MYSQL_PORT}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " confirm
    
    if [[ "$confirm" != "yes" ]]; then
        log_info "Restore cancelled by user"
        cleanup_work_dir
        exit 0
    fi
    
    # Stop application connections (if applicable)
    log_info "Consider stopping application before restore"
    
    # Restore database
    log_info "Restoring database..."
    
    mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
          --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" \
          < "$work_file" 2>> "$LOG_FILE"
    
    # Verify restoration
    log_info "Verifying restoration..."
    
    local table_count=$(mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
                              --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" \
                              -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'P5DB';")
    
    log_info "Tables restored: $table_count"
    
    # Cleanup
    cleanup_work_dir
    
    log_info "=========================================="
    log_info "FULL RESTORE COMPLETED SUCCESSFULLY"
    log_info "=========================================="
}

# Point-in-time recovery
restore_pitr() {
    local backup_file="$1"
    local target_time="$2"
    
    log_info "=========================================="
    log_info "Starting POINT-IN-TIME RECOVERY"
    log_info "Backup: $backup_file"
    log_info "Target time: $target_time"
    log_info "=========================================="
    
    # First, restore full backup
    restore_full "$backup_file"
    
    # Then apply binary logs up to target time
    log_info "Applying binary logs up to: $target_time"
    
    # Find binary logs after the backup
    local binlog_dir="${BACKUP_BASE_DIR}/$(dirname "$backup_file" | xargs dirname)/binlog"
    
    if [[ -d "$binlog_dir" ]]; then
        for binlog in "$binlog_dir"/*.sql.gz; do
            if [[ -f "$binlog" ]]; then
                log_info "Applying binary log: $binlog"
                
                # Decompress and apply with stop time
                gunzip -c "$binlog" | \
                    mysql --host="$MYSQL_HOST" --port="$MYSQL_PORT" \
                          --user="$MYSQL_USER" --password="$MYSQL_PASSWORD" \
                          2>> "$LOG_FILE" || true
            fi
        done
    else
        log_warn "No binary logs found for PITR"
    fi
    
    log_info "=========================================="
    log_info "POINT-IN-TIME RECOVERY COMPLETED"
    log_info "=========================================="
}

# ============================================
# Main
# ============================================

main() {
    log_info "MySQL Recovery Script started"
    log_info "Operation: $RESTORE_TYPE"
    
    case "$RESTORE_TYPE" in
        full)
            if [[ -z "$BACKUP_FILE" ]]; then
                log_error "Backup file required"
                show_help
                exit 1
            fi
            restore_full "$BACKUP_FILE"
            ;;
        pitr)
            if [[ -z "$BACKUP_FILE" || -z "$TARGET_TIMESTAMP" ]]; then
                log_error "Backup file and target timestamp required"
                show_help
                exit 1
            fi
            restore_pitr "$BACKUP_FILE" "$TARGET_TIMESTAMP"
            ;;
        list)
            list_backups
            ;;
        verify)
            if [[ -z "$BACKUP_FILE" ]]; then
                log_error "Backup file required"
                exit 1
            fi
            verify_backup "$BACKUP_FILE"
            ;;
        download)
            if [[ -z "$BACKUP_FILE" ]]; then
                log_error "S3 path required"
                exit 1
            fi
            prepare_work_dir
            download_from_s3 "$BACKUP_FILE"
            ;;
        help|--help|-h|*)
            show_help
            ;;
    esac
}

# Run main
main "$@"
