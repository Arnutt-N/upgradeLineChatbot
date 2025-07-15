#!/usr/bin/env python3
"""
WebSocket Test Script for Admin Chat
ทดสอบการทำงานของ WebSocket และการส่งข้อความ
"""

import asyncio
import json
import websockets
from datetime import datetime

async def test_websocket_connection():
    """ทดสอบการเชื่อมต่อ WebSocket"""
    uri = "ws://localhost:8000/ws"  # ปรับ URL ตามที่ใช้งานจริง
    
    try:
        print(f"🔌 Connecting to WebSocket: {uri}")
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # ส่งข้อความทดสอบ
            test_message = {
                "type": "test_message",
                "message": "Test from Python script",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")
            
            # รอรับข้อความ
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📥 Received response: {response}")
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
            # ส่งข้อความจำลอง user message
            user_message = {
                "type": "new_message",
                "userId": "test_user_123",
                "message": "สวัสดีครับ นี่คือข้อความทดสอบ",
                "displayName": "ผู้ใช้ทดสอบ",
                "pictureUrl": None,
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(user_message, ensure_ascii=False))
            print(f"📤 Sent simulated user message: {user_message}")
            
            # รอสักครู่
            await asyncio.sleep(2)
            
            print("✅ WebSocket test completed successfully!")
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        print(f"Error type: {type(e).__name__}")

async def test_broadcast_message():
    """ทดสอบการส่ง broadcast message"""
    uri = "ws://localhost:8000/ws"
    
    try:
        print(f"🔌 Testing broadcast functionality...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected for broadcast test")
            
            # ส่งข้อความหลายประเภท
            messages = [
                {
                    "type": "new_message",
                    "userId": "user001",
                    "message": "ข้อความทดสอบ 1",
                    "displayName": "ลูกค้า A",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "bot_response_complete",
                    "userId": "user001", 
                    "message": "คำตอบจากบอท",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "mode_changed",
                    "userId": "user001",
                    "mode": "manual",
                    "message": "🔄 เปลี่ยนเป็นโหมด Manual แล้ว",
                    "timestamp": datetime.now().isoformat()
                }
            ]
            
            for i, msg in enumerate(messages, 1):
                await websocket.send(json.dumps(msg, ensure_ascii=False))
                print(f"📤 Sent test message {i}: {msg['type']}")
                await asyncio.sleep(1)
            
            print("✅ Broadcast test completed!")
            
    except Exception as e:
        print(f"❌ Broadcast test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting WebSocket tests...")
    print("="*50)
    
    # ทดสอบการเชื่อมต่อพื้นฐาน
    asyncio.run(test_websocket_connection())
    
    print("\n" + "="*50)
    
    # ทดสอบ broadcast
    asyncio.run(test_broadcast_message())
    
    print("\n✅ All WebSocket tests completed!")
                # บันทึกข้อความทดสอบลง database
                test_user_id = "debug_test_user"
                test_message = "ข้อความทดสอบสำหรับ debug"
                
                print(f"💾 Saving test message to database...")
                await save_chat_to_history(
                    db=db,
                    user_id=test_user_id,
                    message_type='user',
                    message_content=test_message,
                    session_id=f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                )
                print("✅ Message saved to database")
                
                # ส่ง WebSocket broadcast
                thai_time = get_thai_time()
                broadcast_data = {
                    "type": "new_message",
                    "userId": test_user_id,
                    "message": test_message,
                    "displayName": "ผู้ใช้ทดสอบ Debug",
                    "pictureUrl": None,
                    "timestamp": thai_time.isoformat()
                }
                
                print(f"📡 Broadcasting message via WebSocket...")
                await manager.broadcast(broadcast_data)
                print("✅ Message broadcasted!")
                
                break
            except Exception as e:
                print(f"❌ Error in database operation: {e}")
                break
                
    except Exception as e:
        print(f"❌ Error debugging message flow: {e}")

def check_websocket_endpoint():
    """ตรวจสอบ WebSocket endpoint"""
    try:
        import requests
        
        print("🔍 Checking WebSocket endpoint...")
        
        # ทดสอบ HTTP health check
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Main server is running")
            else:
                print(f"⚠️  Server responding with status: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot reach server: {e}")
            return False
        
        # ตรวจสอบ admin endpoint
        try:
            response = requests.get("http://localhost:8000/admin", timeout=5)
            if response.status_code == 200:
                print("✅ Admin endpoint is accessible")
            else:
                print(f"⚠️  Admin endpoint status: {response.status_code}")
        except Exception as e:
            print(f"❌ Cannot reach admin endpoint: {e}")
        
        return True
        
    except ImportError:
        print("❌ requests library not available")
        return False

async def run_diagnostics():
    """รันการวินิจฉัยปัญหาทั้งหมด"""
    print("🔧 Running Admin Chat Diagnostics...")
    print("=" * 60)
    
    # 1. ตรวจสอบ server
    print("\n1️⃣  Checking Server Status...")
    server_ok = check_websocket_endpoint()
    
    if not server_ok:
        print("❌ Server is not running. Please start the server first:")
        print("   python main.py")
        return
    
    # 2. ตรวจสอบ WebSocket Manager
    print("\n2️⃣  Checking WebSocket Manager...")
    await test_websocket_manager()
    
    # 3. ทดสอบการไหลของข้อความ
    print("\n3️⃣  Testing Message Flow...")
    await debug_message_flow()
    
    # 4. แสดงคำแนะนำ
    print("\n" + "=" * 60)
    print("🎯 การแก้ปัญหาที่แนะนำ:")
    print()
    print("1. 🌐 เปิดหน้าแอดมิน: http://localhost:8000/admin")
    print("2. 🔧 กด F12 เพื่อเปิด Developer Tools")
    print("3. 📊 ดูแท็บ Console หา error message")
    print("4. 🔌 ดูแท็บ Network หา WebSocket connection")
    print("5. 🔄 ลอง refresh หน้าเว็บ")
    print()
    print("📋 สิ่งที่ควรเห็นใน Console:")
    print("   - '✅ WebSocket Connected Successfully'")
    print("   - '📨 Raw WebSocket message received'")
    print("   - '💬 MATCH! Displaying new message for current user'")
    print()
    print("❌ หากยังมีปัญหา:")
    print("   - ตรวจสอบ firewall/antivirus")
    print("   - ลองใช้ browser อื่น")
    print("   - ตรวจสอบ network connection")

if __name__ == "__main__":
    print("🚀 Admin Chat Real-time Update Diagnostics")
    print("🎯 วัตถุประสงค์: แก้ปัญหาหน้าแอดมินไม่แสดงข้อความใหม่ทันที")
    print()
    
    try:
        asyncio.run(run_diagnostics())
    except KeyboardInterrupt:
        print("\n⏹️  Diagnostics interrupted by user")
    except Exception as e:
        print(f"\n❌ Diagnostics failed: {e}")
        print(f"Error type: {type(e).__name__}")
    
    print("\n✅ Diagnostics completed!")
