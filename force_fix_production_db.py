# force_fix_production_db.py
"""
Force fix production database on Render
"""
import os
import sqlite3
import sys

def force_fix_database():
    """Force fix database schema in production"""
    print("🔧 Force fixing production database...")
    
    db_path = "./chatbot.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check current schema
        print("🔍 Checking current database schema...")
        
        # 1. Fix chat_history table
        cursor.execute("PRAGMA table_info(chat_history)")
        columns = [row[1] for row in cursor.fetchall()]
        print(f"chat_history columns: {columns}")
        
        if 'is_processed' not in columns:
            print("🔄 Adding is_processed column to chat_history...")
            try:
                cursor.execute("ALTER TABLE chat_history ADD COLUMN is_processed BOOLEAN DEFAULT 1")
                conn.commit()
                print("✅ is_processed column added")
            except Exception as e:
                print(f"⚠️ Could not add is_processed: {e}")
        
        # 2. Check if we have data in chat_history
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        chat_count = cursor.fetchone()[0]
        print(f"📊 Found {chat_count} records in chat_history")
        
        # 3. Check user_status table
        cursor.execute("SELECT COUNT(*) FROM user_status")
        user_count = cursor.fetchone()[0]
        print(f"👥 Found {user_count} users in user_status")
        
        # 4. Show sample data
        if chat_count > 0:
            cursor.execute("SELECT user_id, message_type, message_content FROM chat_history LIMIT 3")
            samples = cursor.fetchall()
            print("📝 Sample chat data:")
            for sample in samples:
                print(f"  - User: {sample[0][:8]}..., Type: {sample[1]}, Message: {sample[2][:30]}...")
        
        conn.close()
        print("✅ Database inspection completed")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing database: {e}")
        return False

if __name__ == "__main__":
    force_fix_database()
