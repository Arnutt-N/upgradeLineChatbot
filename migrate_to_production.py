# migrate_to_production.py
"""
Production Migration Script with Schema Update
"""
import asyncio
import os
import sys
import sqlite3
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

print("🔧 Loading application modules...")
try:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    from app.db.models import Base
    print("✅ Application modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

async def update_sqlite_schema():
    """Update SQLite schema to fix column issues"""
    print("🔧 Updating SQLite database schema...")
    
    db_path = "./chatbot.db"
    
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            print("📦 Database doesn't exist, will be created fresh")
            return True
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check user_status table structure
        cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'id' not in columns:
            print("🔄 Adding missing id column to user_status...")
            
            # Backup existing data
            cursor.execute("""
                CREATE TABLE user_status_backup AS 
                SELECT * FROM user_status
            """)
            
            # Drop and recreate with correct schema
            cursor.execute("DROP TABLE user_status")
            cursor.execute("""
                CREATE TABLE user_status (
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
            
            # Restore data
            cursor.execute("""
                INSERT INTO user_status (user_id, display_name, picture_url, is_in_live_chat, chat_mode, created_at, updated_at)
                SELECT user_id, display_name, picture_url, is_in_live_chat, chat_mode, created_at, updated_at
                FROM user_status_backup
            """)
            
            # Clean up backup
            cursor.execute("DROP TABLE user_status_backup")
            
            print("✅ user_status schema updated successfully")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Schema update failed: {e}")
        return False

async def migrate_to_production():
    """Main migration function"""
    print("🚀 Starting production database migration...")
    
    # Step 1: Update schema first
    if not await update_sqlite_schema():
        print("❌ Schema update failed, stopping migration")
        return False
    
    # Step 2: Create engine and tables
    DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with engine.begin() as conn:
            print("📦 Creating/updating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully!")
            
        print("🎉 Production migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(migrate_to_production())
    sys.exit(0 if success else 1)
