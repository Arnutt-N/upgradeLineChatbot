#!/usr/bin/env python3
"""
Database Migration Runner
ใช้สำหรับ run migration scripts อัตโนมัติ
"""

import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

def run_migration():
    """Run database migration"""
    print("Starting Database Migration...")
    
    # Database path
    db_path = "chatbot.db"
    migration_file = "migrations/001_add_enhanced_tracking_tables.sql"
    
    if not os.path.exists(migration_file):
        print(f"Migration file not found: {migration_file}")
        return False
    
    try:
        # Connect to database
        print(f"Connecting to database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Backup database first
        backup_path = f"chatbot_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        print(f"Creating backup: {backup_path}")
        
        # Create backup
        backup_conn = sqlite3.connect(backup_path)
        conn.backup(backup_conn)
        backup_conn.close()
        print(f"Backup created successfully!")
        
        # Read migration file
        print(f"Reading migration file: {migration_file}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Execute migration
        print("Executing migration...")
        cursor.executescript(migration_sql)
        conn.commit()
        
        # Verify tables
        print("Verifying new tables...")
        tables_to_check = [
            'chat_history',
            'friend_activity', 
            'telegram_notifications',
            'telegram_settings',
            'system_logs',
            'migration_history'
        ]
        
        for table in tables_to_check:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
            if cursor.fetchone():
                print(f"Table '{table}' created successfully")
            else:
                print(f"Table '{table}' not found!")
                return False
        
        # Check default settings
        cursor.execute("SELECT COUNT(*) FROM telegram_settings;")
        settings_count = cursor.fetchone()[0]
        print(f"Telegram settings: {settings_count} records inserted")
        
        conn.close()
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        return False

def rollback_migration():
    """Rollback migration using backup"""
    print("Rolling back migration...")
    
    # Find latest backup
    backup_files = [f for f in os.listdir('.') if f.startswith('chatbot_backup_') and f.endswith('.db')]
    if not backup_files:
        print("No backup files found!")
        return False
    
    latest_backup = sorted(backup_files)[-1]
    print(f"Using backup: {latest_backup}")
    
    try:
        # Replace current database with backup
        os.replace(latest_backup, "chatbot.db")
        print("Rollback completed successfully!")
        return True
    except Exception as e:
        print(f"Rollback failed: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        success = rollback_migration()
    else:
        success = run_migration()
    
    if success:
        print("\nMigration process completed!")
        sys.exit(0)
    else:
        print("\nMigration process failed!")
        sys.exit(1)
