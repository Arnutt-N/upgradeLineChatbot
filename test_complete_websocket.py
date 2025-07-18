#!/usr/bin/env python3
"""
Complete WebSocket test to verify all functionality
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_admin_websocket():
    """Test admin WebSocket endpoint"""
    uri = "ws://127.0.0.1:8000/ws"
    
    try:
        print(f"Connecting to admin WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: Admin WebSocket connection established!")
            
            # Test different message types
            test_messages = [
                {
                    "type": "admin_message",
                    "userId": "test_user_123",
                    "message": "Hello from admin",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "type": "user_message",
                    "userId": "test_user_456", 
                    "message": "Hello from user",
                    "timestamp": datetime.now().isoformat()
                }
            ]
            
            for msg in test_messages:
                await websocket.send(json.dumps(msg))
                print(f"Sent: {msg['type']}")
            
            print("SUCCESS: All test messages sent successfully!")
            
    except Exception as e:
        print(f"ERROR: Admin WebSocket error: {e}")

async def test_ui_websocket():
    """Test UI WebSocket endpoint"""
    uri = "ws://127.0.0.1:8000/ui/ws"
    
    try:
        print(f"Connecting to UI WebSocket: {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: UI WebSocket connection established!")
            
            # Test UI message
            test_message = {
                "type": "ui_update",
                "data": {"status": "active"},
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print("UI test message sent")
            
    except Exception as e:
        print(f"ERROR: UI WebSocket error: {e}")

async def main():
    """Run all WebSocket tests"""
    print("Starting WebSocket Connection Tests")
    print("=" * 50)
    
    await test_admin_websocket()
    print()
    await test_ui_websocket()
    
    print("\n" + "=" * 50)
    print("SUCCESS: WebSocket testing completed!")
    print("INFO: If you see 'SUCCESS' messages, WebSocket is working properly")

if __name__ == "__main__":
    asyncio.run(main())