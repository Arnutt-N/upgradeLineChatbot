# update_database_schema.py
"""
Update database schema to fix column issues
"""
import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def update_schema():
    """Update database schema to match new models"""
    print("🔧 Updating database schema...")
    
    # Use direct SQLite connection for schema changes
    db_path = "./chatbot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if user_status table needs updating
        cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in cursor.fetchall()]
        
        print(f"Current user_status columns: {columns}")
        
        if 'id' not in columns:
            print("Adding id column to user_status...")
            
            # Create new table with correct schema
            cursor.execute("""
                CREATE TABLE user_status_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT UNIQUE NOT NULL,
                    display_name TEXT,
                    picture_url TEXT,
                    is_in_live_chat BOOLEAN DEFAULT 0,
                    chat_mode TEXT DEFAULT 'manual',
                    user_metadata TEXT,
                    preferences TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME
                )
            """)
            
            # Copy existing data
            cursor.execute("""
                INSERT INTO user_status_new (user_id, display_name, picture_url, is_in_live_chat, chat_mode, created_at, updated_at)
                SELECT user_id, display_name, picture_url, is_in_live_chat, chat_mode, created_at, updated_at
                FROM user_status
            """)
            
            # Replace old table
            cursor.execute("DROP TABLE user_status")
            cursor.execute("ALTER TABLE user_status_new RENAME TO user_status")
            
            print("✅ user_status table updated successfully")
        else:
            print("✅ user_status table schema is already correct")
        
        # Create missing tables if needed
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS friend_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                additional_data TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Database schema updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating schema: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(update_schema())
    if success:
        print("🎉 Schema update completed!")
    else:
        print("💥 Schema update failed!")
