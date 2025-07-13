#!/usr/bin/env python3
"""
Verify Migration Results
ตรวจสอบผลลัพธ์การ Migration
"""

import sqlite3

def verify_migration():
    """ตรวจสอบผลลัพธ์การ migration"""
    print("Verifying Migration Results...")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # ตรวจสอบตารางที่มีทั้งหมด
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
        tables = cursor.fetchall()
        
        print("All Tables in Database:")
        for i, (table_name,) in enumerate(tables, 1):
            print(f"{i:2d}. {table_name}")
        
        print("\n" + "=" * 50)
        
        # ตรวจสอบตารางใหม่โดยเฉพาะ
        new_tables = [
            'chat_history',
            'friend_activity', 
            'telegram_notifications',
            'telegram_settings',
            'system_logs',
            'migration_history'
        ]
        
        print("New Tables Status:")
        for table in new_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            print(f"OK {table}: {count} records")
        
        print("\n" + "=" * 50)
        
        # ตรวจสอบ Telegram Settings โดยละเอียด
        print("Telegram Settings Details:")
        cursor.execute("SELECT setting_key, setting_value, setting_type FROM telegram_settings ORDER BY id;")
        settings = cursor.fetchall()
        
        for key, value, setting_type in settings:
            print(f"  {key}: {value} ({setting_type})")
        
        print("\n" + "=" * 50)
        
        # ตรวจสอบ Migration History
        print("Migration History:")
        cursor.execute("SELECT migration_name, executed_at, success FROM migration_history ORDER BY executed_at;")
        migrations = cursor.fetchall()
        
        for name, executed_at, success in migrations:
            status = "SUCCESS" if success else "FAILED"
            print(f"  {name}: {status} at {executed_at}")
        
        conn.close()
        
        print("\n" + "=" * 50)
        print("Migration Verification Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"Error during verification: {str(e)}")
        return False

if __name__ == "__main__":
    verify_migration()
