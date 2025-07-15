#!/usr/bin/env python3
"""
Admin Chat Debug Script
แก้ปัญหาหน้าแอดมินไม่แสดงข้อความใหม่ทันที
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def debug_admin_chat():
    """Debug หน้าแอดมินแชท"""
    print("🔧 Admin Chat Debug Starting...")
    
    try:
        # Import modules
        from app.services.ws_manager import manager
        from app.db.database import get_db
        from app.utils.timezone import get_thai_time
        
        print(f"📊 Current active WebSocket connections: {len(manager.active_connections)}")
        
        if len(manager.active_connections) == 0:
            print("⚠️  WARNING: No active WebSocket connections!")
            print("💡 Solution: Open admin page at http://localhost:8000/admin")
            return
        
        # สร้างข้อความทดสอบ
        test_data = {
            "type": "new_message",
            "userId": "debug_user_001", 
            "message": "🧪 Debug Test Message - " + datetime.now().strftime("%H:%M:%S"),
            "displayName": "Debug User",
            "pictureUrl": None,
            "timestamp": get_thai_time().isoformat()
        }
        
        print("📤 Sending test message via WebSocket...")
        await manager.broadcast(test_data)
        print("✅ Test message sent!")
        
        # ส่งข้อความเพิ่มเติม
        await asyncio.sleep(2)
        
        bot_response = {
            "type": "bot_response_complete",
            "userId": "debug_user_001",
            "message": "🤖 Bot Test Response - " + datetime.now().strftime("%H:%M:%S"), 
            "timestamp": get_thai_time().isoformat()
        }
        
        print("📤 Sending bot response test...")
        await manager.broadcast(bot_response)
        print("✅ Bot response sent!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")

def print_instructions():
    """แสดงคำแนะนำการแก้ปัญหา"""
    print("\n" + "="*60)
    print("🎯 คำแนะนำการแก้ปัญหา")
    print("="*60)
    print()
    print("1. 🚀 เริ่มต้น Server:")
    print("   cd D:\\hrProject\\upgradeLineChatbot")
    print("   python main.py")
    print()
    print("2. 🌐 เปิดหน้าแอดมิน:")
    print("   http://localhost:8000/admin")
    print()
    print("3. 🔧 เปิด Developer Tools (F12):")
    print("   - ดูแท็บ Console หา error")
    print("   - ดูแท็บ Network หา WebSocket connection")
    print()
    print("4. 🔍 ตรวจสอบในหน้าแอดมิน:")
    print("   - สถานะการเชื่อมต่อ (มุมขวาบน)")
    print("   - Console log ที่แสดง WebSocket messages")
    print()
    print("5. 🧪 รัน Debug Script:")
    print("   python debug_admin_chat.py")
    print()

if __name__ == "__main__":
    print_instructions()
    
    try:
        asyncio.run(debug_admin_chat())
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ Debug completed!")
