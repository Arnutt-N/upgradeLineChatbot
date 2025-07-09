#!/usr/bin/env python3
"""
Migration script to add display_name column to user_status table
Run this once to update existing database
"""
import asyncio
import aiosqlite
import os

async def migrate_database():
    """Add display_name column to existing database"""
    db_path = "chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} not found!")
        return
    
    try:
        async with aiosqlite.connect(db_path) as db:
            # Check if column already exists
            cursor = await db.execute("PRAGMA table_info(user_status)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'display_name' in column_names:
                print("✅ display_name column already exists")
                return
            
            print("🔄 Adding display_name column to user_status table...")
            
            # Add the new column
            await db.execute("ALTER TABLE user_status ADD COLUMN display_name TEXT")
            
            # Update existing users with fallback names
            await db.execute("""
                UPDATE user_status 
                SET display_name = 'ลูกค้า ' || substr(user_id, -6)
                WHERE display_name IS NULL
            """)
            
            await db.commit()
            print("✅ Migration completed successfully!")
            
            # Verify the migration
            cursor = await db.execute("SELECT user_id, display_name FROM user_status")
            users = await cursor.fetchall()
            print(f"📊 Updated {len(users)} users:")
            for user in users:
                print(f"   - {user[0]} -> {user[1]}")
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    asyncio.run(migrate_database())
    print("🎉 Migration process completed!")
