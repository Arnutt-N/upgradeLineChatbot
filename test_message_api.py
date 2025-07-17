# Test API endpoint to check message loading
import asyncio
import httpx
import json

async def test_message_loading():
    """Test the /admin/messages API endpoint"""
    base_url = "http://localhost:8000"
    user_id = "U693cb72c4dff8525756775d5fce45296"  # From your data
    
    async with httpx.AsyncClient() as client:
        # Test with different limits
        for limit in [10, 50, 100, 200, 500]:
            try:
                url = f"{base_url}/admin/messages/{user_id}?limit={limit}&offset=0"
                print(f"\n🔍 Testing: {url}")
                
                response = await client.get(url, timeout=30.0)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    messages = data.get('messages', [])
                    print(f"   Messages returned: {len(messages)}")
                    print(f"   Total in response: {data.get('total', 'N/A')}")
                    
                    # Show first and last message
                    if messages:
                        first = messages[0]
                        last = messages[-1]
                        print(f"   First: [{first['sender_type']}] {first['message'][:30]}...")
                        print(f"   Last:  [{last['sender_type']}] {last['message'][:30]}...")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Exception: {e}")
        
        # Test if messages are properly formatted
        print("\n📋 Checking message format...")
        response = await client.get(f"{base_url}/admin/messages/{user_id}?limit=5&offset=0")
        if response.status_code == 200:
            data = response.json()
            for i, msg in enumerate(data.get('messages', [])[:3]):
                print(f"\nMessage {i+1}:")
                print(f"  ID: {msg.get('id', 'N/A')}")
                print(f"  Type: {msg.get('sender_type', 'N/A')}")
                print(f"  Message: {msg.get('message', 'N/A')[:50]}...")
                print(f"  Time: {msg.get('created_at', 'N/A')}")

if __name__ == "__main__":
    print("🧪 Testing Message Loading API")
    print("=" * 50)
    asyncio.run(test_message_loading())
