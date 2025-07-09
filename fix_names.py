# -*- coding: utf-8 -*-
import sqlite3
import os

def fix_display_names():
    """Fix display names with proper encoding"""
    db_path = "D:/hrProject/upgradeLineChatbot/chatbot.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update existing users with properly encoded fallback names
        cursor.execute("""
            UPDATE user_status 
            SET display_name = 'Customer ' || substr(user_id, -6)
        """)
        
        conn.commit()
        print("Fixed display names successfully!")
        
        # Verify the fix
        cursor.execute("SELECT user_id, display_name FROM user_status")
        users = cursor.fetchall()
        print(f"Current users:")
        for user in users:
            print(f"   - {user[0]} -> {user[1]}")
        
        conn.close()
            
    except Exception as e:
        print(f"Fix failed: {e}")

if __name__ == "__main__":
    fix_display_names()
