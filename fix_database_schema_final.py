# fix_database_schema_final.py
"""
Final database schema fix for production
"""
import asyncio
import sqlite3
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def fix_database_schema():
    """Fix all database schema issues"""
    print("🔧 Fixing database schema issues...")
    
    db_path = "./chatbot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. Fix chat_history table - add missing is_processed column
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_processed' not in columns:
            print("🔄 Adding is_processed column to chat_history...")
            cursor.execute("ALTER TABLE chat_history ADD COLUMN is_processed BOOLEAN DEFAULT 1")
            print("✅ is_processed column added")
        
        # 2. Fix system_logs table - change log_level to level
        cursor.execute("PRAGMA table_info(system_logs)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'log_level' in columns and 'level' not in columns:
            print("🔄 Fixing system_logs column name...")
            cursor.execute("""
                CREATE TABLE system_logs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_id TEXT,
                    additional_data TEXT
                )
            """)
            
            cursor.execute("""
                INSERT INTO system_logs_new (level, message, timestamp, user_id, additional_data)
                SELECT log_level, message, timestamp, user_id, additional_data
                FROM system_logs
            """)
            
            cursor.execute("DROP TABLE system_logs")
            cursor.execute("ALTER TABLE system_logs_new RENAME TO system_logs")
            print("✅ system_logs table fixed")
        
        # 3. Create missing tables
        missing_tables = [
            "telegram_notifications",
            "telegram_settings", 
            "form_submissions",
            "form_attachments",
            "admin_users",
            "form_status_history",
            "shared_notifications",
            "shared_audit_logs"
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in missing_tables:
            if table not in existing_tables:
                print(f"📦 Creating missing table: {table}")
                if table == "telegram_notifications":
                    cursor.execute("""
                        CREATE TABLE telegram_notifications (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id TEXT NOT NULL,
                            notification_type TEXT NOT NULL,
                            message TEXT NOT NULL,
                            sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            telegram_message_id TEXT,
                            status TEXT DEFAULT 'pending'
                        )
                    """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema fixed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_database_schema())
    if success:
        print("🎉 Schema fix completed!")
    else:
        print("💥 Schema fix failed!")
