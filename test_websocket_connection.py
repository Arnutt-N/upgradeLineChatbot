#!/usr/bin/env python3
"""
Test WebSocket connection to diagnose the connection issue
"""
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection to the server"""
    uri = "ws://127.0.0.1:8000/ws"
    
    try:
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("SUCCESS: WebSocket connection established!")
            
            # Send a test message
            test_message = {
                "type": "test",
                "message": "Hello from test client",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            print("Test message sent")
            
            # Listen for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"Received response: {response}")
            except asyncio.TimeoutError:
                print("No response received (timeout)")
            
            print("WebSocket test completed successfully!")
            
    except ConnectionRefusedError:
        print("ERROR: Connection refused - Server is not running")
    except Exception as e:
        print(f"ERROR: WebSocket connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket_connection())