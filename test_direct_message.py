#!/usr/bin/env python3
"""
Direct Message Test for Admin Chat System
ทดสอบการส่งข้อความโดยตรงไปยังระบบเพื่อดู WebSocket broadcast
"""

import asyncio
import json
import requests
from datetime import datetime
import time

def test_direct_message():
    """ทดสอบการส่งข้อความผ่าน API โดยตรง"""
    
    base_url = "http://localhost:8000"  # ปรับ URL ตามที่ใช้งานจริง
    
    print("🚀 Testing direct message to admin system...")
    
    # ทดสอบการส่งข้อความจากแอดมิน
    admin_message_data = {
        "user_id": "test_user_12345",
        "message": "สวัสดีครับ นี่คือข้อความทดสอบจากแอดมิน"
    }
    
    try:
        print(f"📤 Sending admin message: {admin_message_data}")
        response = requests.post(
            f"{base_url}/admin/reply",
            headers={"Content-Type": "application/json"},
            json=admin_message_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Admin message sent successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Admin message failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error sending admin message: {e}")
    
    time.sleep(2)
    
    # ทดสอบการโหลดรายชื่อผู้ใช้
    try:
        print("📊 Testing user list loading...")
        response = requests.get(f"{base_url}/admin/users", timeout=10)
        
        if response.status_code == 200:
            users_data = response.json()
            print("✅ Users loaded successfully!")
            print(f"Found {len(users_data.get('users', []))} users")
            for user in users_data.get('users', [])[:3]:  # Show first 3 users
                print(f"  - {user.get('display_name', 'Unknown')} ({user.get('user_id', '')})")
        else:
            print(f"❌ Failed to load users: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error loading users: {e}")
    
    time.sleep(2)
    
    # ทดสอบการโหลดข้อความ
    try:
        test_user_id = "test_user_12345"
        print(f"💬 Testing message loading for user: {test_user_id}")
        response = requests.get(f"{base_url}/admin/messages/{test_user_id}", timeout=10)
        
        if response.status_code == 200:
            messages_data = response.json()
            print("✅ Messages loaded successfully!")
            print(f"Found {len(messages_data.get('messages', []))} messages")
            for msg in messages_data.get('messages', [])[-3:]:  # Show last 3 messages
                print(f"  - [{msg.get('sender_type', 'Unknown')}] {msg.get('message', '')[:50]}...")
        else:
            print(f"❌ Failed to load messages: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error loading messages: {e}")

def test_system_status():
    """ทดสอบสถานะระบบ"""
    
    base_url = "http://localhost:8000"
    
    try:
        print("🔍 Checking system status...")
        response = requests.get(f"{base_url}/admin/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            print("✅ System status retrieved successfully!")
            print(f"  - AI Available: {status.get('ai_available', False)}")
            print(f"  - Database Available: {status.get('database_available', False)}")
            print(f"  - LINE Configured: {status.get('line_configured', False)}")
            print(f"  - Telegram Configured: {status.get('telegram_configured', False)}")
        else:
            print(f"❌ Failed to get system status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking system status: {e}")

if __name__ == "__main__":
    print("🧪 Starting direct message tests...")
    print("="*60)
    
    # ทดสอบสถานะระบบ
    test_system_status()
    print("\n" + "-"*60)
    
    # ทดสอบการส่งข้อความ
    test_direct_message()
    
    print("\n" + "="*60)
    print("✅ All direct message tests completed!")
    print("\n💡 หากการทดสอบผ่าน แต่หน้าแอดมินยังไม่แสดงข้อความใหม่:")
    print("   1. ตรวจสอบ Browser Console (F12) หา error")
    print("   2. ตรวจสอบ WebSocket connection ในแท็บ Network")
    print("   3. ลอง refresh หน้าเว็บ")
    print("   4. ตรวจสอบว่า WebSocket endpoint /ws ทำงานถูกต้อง")
