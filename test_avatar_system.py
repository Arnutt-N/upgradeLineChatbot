#!/usr/bin/env python3
# test_avatar_system.py - Test the new avatar system

import sqlite3
import os

print("🧪 Testing Avatar System")
print("=" * 40)

try:
    # ตรวจสอบ database
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    print("1. Testing database schema...")
    cursor.execute("PRAGMA table_info(user_status)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "picture_url" in columns:
        print("   [OK] picture_url column exists")
    else:
        print("   [ERROR] picture_url column missing!")
        exit(1)
    
    print("2. Testing sample data...")
    
    # เพิ่มข้อมูลทดสอบ
    test_user_id = "test_user_123"
    test_display_name = "Test User"
    test_picture_url = "https://example.com/avatar.jpg"
    
    # ลบข้อมูลเดิมถ้ามี
    cursor.execute("DELETE FROM user_status WHERE user_id = ?", (test_user_id,))
    
    # เพิ่มข้อมูลทดสอบ
    cursor.execute("""
        INSERT INTO user_status (user_id, display_name, picture_url, is_in_live_chat, chat_mode)
        VALUES (?, ?, ?, ?, ?)
    """, (test_user_id, test_display_name, test_picture_url, False, 'manual'))
    
    conn.commit()
    print("   [OK] Test data inserted")
    
    # ตรวจสอบข้อมูล
    cursor.execute("""
        SELECT user_id, display_name, picture_url, is_in_live_chat, chat_mode
        FROM user_status WHERE user_id = ?
    """, (test_user_id,))
    
    result = cursor.fetchone()
    if result:
        user_id, display_name, picture_url, is_in_live_chat, chat_mode = result
        print(f"   User ID: {user_id}")
        print(f"   Display Name: {display_name}")
        print(f"   Picture URL: {picture_url}")
        print(f"   In Live Chat: {is_in_live_chat}")
        print(f"   Chat Mode: {chat_mode}")
        print("   [OK] Data retrieved successfully")
    else:
        print("   [ERROR] Failed to retrieve test data")
        exit(1)
    
    print("3. Testing all users data...")
    cursor.execute("""
        SELECT user_id, display_name, picture_url 
        FROM user_status 
        LIMIT 5
    """)
    users = cursor.fetchall()
    
    print(f"   Total users found: {len(users)}")
    for user in users:
        user_id, display_name, picture_url = user
        pic_status = "Has Picture" if picture_url else "No Picture"
        print(f"   - {user_id}: {display_name} ({pic_status})")
    
    # ลบข้อมูลทดสอบ
    cursor.execute("DELETE FROM user_status WHERE user_id = ?", (test_user_id,))
    conn.commit()
    print("   [OK] Test data cleaned up")
    
    conn.close()
    
    print("\n✅ All tests passed!")
    print("🎉 Avatar system is ready!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
