#!/usr/bin/env python3
# test_db.py - Simple database test

import sqlite3
import os

print("Starting database test...")

# ตรวจสอบไฟล์ database
db_file = "chatbot.db"
if os.path.exists(db_file):
    print(f"[OK] Database file found: {db_file}")
    print(f"     Size: {os.path.getsize(db_file)} bytes")
else:
    print(f"[ERROR] Database file not found: {db_file}")
    exit(1)

try:
    # เชื่อมต่อ database
    print("Connecting to database...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # ตรวจสอบ tables
    print("Checking tables...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables found: {[t[0] for t in tables]}")
    
    # ตรวจสอบ user_status schema
    print("\nChecking user_status schema...")
    cursor.execute("PRAGMA table_info(user_status)")
    columns = cursor.fetchall()
    
    print("Columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # ตรวจสอบ picture_url
    column_names = [col[1] for col in columns]
    print(f"\nPicture URL column exists: {'picture_url' in column_names}")
    
    # ถ้าไม่มี ให้เพิ่ม
    if "picture_url" not in column_names:
        print("Adding picture_url column...")
        cursor.execute("ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL")
        conn.commit()
        print("[OK] Column added!")
        
        # ตรวจสอบอีกครั้ง
        cursor.execute("PRAGMA table_info(user_status)")
        new_columns = cursor.fetchall()
        print("Updated columns:")
        for col in new_columns:
            print(f"  - {col[1]} ({col[2]})")
    
    # แสดงข้อมูล
    cursor.execute("SELECT COUNT(*) FROM user_status")
    count = cursor.fetchone()[0]
    print(f"\nTotal users: {count}")
    
    conn.close()
    print("[OK] Test completed successfully!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
