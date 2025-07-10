# migrate_add_picture_url.py - Simple migration script
import sys
import os

# เพิ่ม path ของโปรเจค
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import sqlite3
from datetime import datetime
import shutil

async def migrate_add_picture_url():
    """เพิ่ม picture_url column ลงใน user_status table"""
    
    print("🚀 Starting Migration: Add picture_url column")
    print("=" * 50)
    
    # ตรวจสอบว่าไฟล์ database มีอยู่หรือไม่
    if not os.path.exists("chatbot.db"):
        print("❌ chatbot.db not found!")
        return False
    
    try:
        # Backup database
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"chatbot_backup_migration_{timestamp}.db"
        shutil.copy2("chatbot.db", backup_name)
        print(f"✅ Backup created: {backup_name}")
        
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # ตรวจสอบว่า column picture_url มีอยู่แล้วหรือไม่
        cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if "picture_url" in columns:
            print("✅ picture_url column already exists!")
            conn.close()
            return True
        
        # เพิ่ม column ใหม่
        cursor.execute("ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL")
        conn.commit()
        
        print("✅ Added picture_url column successfully")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute("PRAGMA table_info(user_status)")
        columns = cursor.fetchall()
        
        print("\n📊 Updated table schema:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]} ({'NULL' if col[3] == 0 else 'NOT NULL'})")
        
        # ตรวจสอบข้อมูลที่มีอยู่
        cursor.execute("SELECT COUNT(*) FROM user_status")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total users: {count}")
        
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(migrate_add_picture_url())
