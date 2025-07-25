#!/usr/bin/env python3
"""
Simple migration script using standard sqlite3
"""
import sqlite3
import os

def migrate_database():
    """Add display_name column to existing database"""
    db_path = "D:/hrProject/upgradeLineChatbot/chatbot.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(user_status)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'display_name' in column_names:
            print("display_name column already exists")
            return
        
        print("Adding display_name column to user_status table...")
        
        # Add the new column
        cursor.execute("ALTER TABLE user_status ADD COLUMN display_name TEXT")
        
        # Update existing users with fallback names
        cursor.execute("""
            UPDATE user_status 
            SET display_name = 'ลูกค้า ' || substr(user_id, -6)
            WHERE display_name IS NULL
        """)
        
        conn.commit()
        print("Migration completed successfully!")
        
        # Verify the migration
        cursor.execute("SELECT user_id, display_name FROM user_status")
        users = cursor.fetchall()
        print(f"Updated {len(users)} users:")
        for user in users:
            print(f"   - {user[0]} -> {user[1]}")
        
        conn.close()
            
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    print("Starting database migration...")
    migrate_database()
    print("Migration process completed!")
