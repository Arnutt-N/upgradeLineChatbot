# migrate_to_production.py
"""
Production Migration Script with Complete Schema Fix
"""
import asyncio
import os
import sys
import sqlite3
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

print("🔧 Starting production migration...")

async def fix_schema_and_migrate():
    """Complete schema fix and migration"""
    
    # 1. Fix existing database schema
    print("🔧 Fixing database schema...")
    db_path = "./chatbot.db"
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Fix chat_history table
            cursor.execute("PRAGMA table_info(chat_history)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'is_processed' not in columns:
                print("Adding is_processed column...")
                cursor.execute("ALTER TABLE chat_history ADD COLUMN is_processed BOOLEAN DEFAULT 1")
            
            # Fix system_logs table
            cursor.execute("PRAGMA table_info(system_logs)")
            sys_columns = [row[1] for row in cursor.fetchall()]
            
            if 'log_level' in sys_columns and 'level' not in sys_columns:
                print("Fixing system_logs column...")
                cursor.execute("ALTER TABLE system_logs RENAME COLUMN log_level TO level")
            
            conn.commit()
            conn.close()
            print("✅ Schema fixed successfully!")
            
        except Exception as e:
            print(f"⚠️ Schema fix warning: {e}")
    
    # 2. Create engine and run SQLAlchemy migration
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.db.models import Base
        
        DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.begin() as conn:
            print("📦 Creating/updating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created/updated successfully!")
            
        await engine.dispose()
        print("🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(fix_schema_and_migrate())
    sys.exit(0 if success else 1)
