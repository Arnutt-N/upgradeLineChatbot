# Test script to simulate message sending and check if it's saved
import asyncio
import httpx
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_001"
TEST_MESSAGE = f"Test message at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

async def test_message_flow():
    """Test the complete message flow"""
    async with httpx.AsyncClient() as client:
        print(f"🚀 Testing message flow...")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"👤 Test User ID: {TEST_USER_ID}")
        print(f"💬 Test Message: {TEST_MESSAGE}")
        print("-" * 50)
        
        # 1. Check health
        try:
            health_resp = await client.get(f"{BASE_URL}/health")
            print(f"✅ Health Check: {health_resp.status_code}")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            return
        
        # 2. Send admin reply
        try:
            reply_data = {
                "user_id": TEST_USER_ID,
                "message": f"Admin reply: {TEST_MESSAGE}"
            }
            reply_resp = await client.post(
                f"{BASE_URL}/admin/reply",
                json=reply_data
            )
            print(f"✅ Admin Reply: {reply_resp.status_code}")
            if reply_resp.status_code != 200:
                print(f"   Response: {reply_resp.text}")
        except Exception as e:
            print(f"❌ Admin Reply Failed: {e}")
        
        # 3. Load messages
        try:
            messages_resp = await client.get(
                f"{BASE_URL}/admin/messages/{TEST_USER_ID}?limit=10"
            )
            print(f"✅ Load Messages: {messages_resp.status_code}")
            if messages_resp.status_code == 200:
                data = messages_resp.json()
                print(f"   Found {len(data.get('messages', []))} messages")
                for msg in data.get('messages', [])[:3]:
                    print(f"   - [{msg['sender_type']}] {msg['message'][:50]}...")
        except Exception as e:
            print(f"❌ Load Messages Failed: {e}")

if __name__ == "__main__":
    print("🧪 LINE Chatbot Message Flow Test")
    print("=" * 50)
    asyncio.run(test_message_flow())
    print("\n✅ Test completed!")
