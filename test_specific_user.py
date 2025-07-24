# Test specific user messages
import asyncio
import httpx

async def test_user_messages():
    base_url = "http://localhost:8002"
    user_id = "U1234567890abcdef1234567890abcdef"
    
    async with httpx.AsyncClient() as client:
        print(f"Testing messages for user: {user_id}")
        
        response = await client.get(f"{base_url}/admin/messages/{user_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Messages found: {len(data.get('messages', []))}")
            
            for msg in data.get('messages', []):
                print(f"  - {msg.get('sender_type', 'unknown')}: {msg.get('message', 'No message')}")
        else:
            print(f"Error: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_user_messages())
