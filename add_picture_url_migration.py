#!/usr/bin/env python3
"""
Database Migration Script: Add picture_url column to user_status table
Created: 2025-07-10
Purpose: Safely add picture_url column without affecting existing data
"""

import asyncio
import sqlite3
from pathlib import Path
import shutil
from datetime import datetime

async def backup_database():
    """สำรองฐานข้อมูลก่อนทำ migration"""
    db_path = Path("chatbot.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return False
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"chatbot_backup_before_migration_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

async def check_column_exists():
    """ตรวจสอบว่า picture_url column มีอยู่แล้วหรือไม่"""
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # ตรวจสอบ schema ของ table user_status
        cursor.execute("PRAGMA table_info(user_status)")
        columns = [row[1] for row in cursor.fetchall()]
        
        conn.close()
        
        return "picture_url" in columns
    except Exception as e:
        print(f"❌ Error checking column: {e}")
        return False

async def add_picture_url_column():
    """เพิ่ม picture_url column ลงใน user_status table"""
    try:
        # ตรวจสอบว่า column มีอยู่แล้วหรือไม่
        if await check_column_exists():
            print("✅ picture_url column already exists!")
            return True
        
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # เพิ่ม column ใหม่ (ใช้ NULL เป็นค่าเริ่มต้น)
        cursor.execute("""
            ALTER TABLE user_status 
            ADD COLUMN picture_url TEXT NULL
        """)
        
        conn.commit()
        conn.close()
        
        print("✅ Successfully added picture_url column to user_status table")
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

async def verify_migration():
    """ตรวจสอบว่า migration สำเร็จ"""
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # ตรวจสอบ schema
        cursor.execute("PRAGMA table_info(user_status)")
        columns = cursor.fetchall()
        
        print("\n📊 Current user_status table schema:")
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            nullable = "NULL" if col[3] == 0 else "NOT NULL"
            print(f"  - {col_name}: {col_type} ({nullable})")
        
        # ตรวจสอบข้อมูลที่มีอยู่
        cursor.execute("SELECT COUNT(*) FROM user_status")
        count = cursor.fetchone()[0]
        print(f"\n📈 Total users in database: {count}")
        
        if count > 0:
            cursor.execute("SELECT user_id, display_name, picture_url FROM user_status LIMIT 3")
            rows = cursor.fetchall()
            print(f"\n🔍 Sample data:")
            for row in rows:
                print(f"  - {row[0]}: {row[1]} (picture: {row[2] or 'NULL'})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

async def main():
    """Main migration function"""
    print("🚀 Starting Database Migration: Add picture_url column")
    print("=" * 60)
    
    # Step 1: Backup
    print("\n📦 Step 1: Creating backup...")
    if not await backup_database():
        print("❌ Migration aborted due to backup failure")
        return False
    
    # Step 2: Add column
    print("\n🔧 Step 2: Adding picture_url column...")
    if not await add_picture_url_column():
        print("❌ Migration failed")
        return False
    
    # Step 3: Verify
    print("\n✅ Step 3: Verifying migration...")
    if not await verify_migration():
        print("❌ Verification failed")
        return False
    
    print("\n🎉 Migration completed successfully!")
    print("=" * 60)
    print("✅ picture_url column added to user_status table")
    print("✅ Existing data preserved")
    print("✅ Ready for next step: Update LINE handler")
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
