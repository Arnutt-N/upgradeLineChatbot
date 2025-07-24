# Test Admin API Endpoints
import asyncio
import httpx
from datetime import datetime

async def test_admin_endpoints():
    """ทดสอบ Admin API endpoints"""
    
    base_url = "http://localhost:8001"
    
    print("Testing Admin API Endpoints")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Health check
        print("\n1. Testing Health Check...")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Health check failed: {e}")
        
        # Test 2: Admin users endpoint
        print("\n2. Testing Admin Users...")
        try:
            response = await client.get(f"{base_url}/admin/users")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Users found: {len(data.get('users', []))}")
                for user in data.get('users', [])[:3]:  # Show first 3 users
                    print(f"  - {user.get('user_id', 'N/A')}: {user.get('display_name', 'No name')}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Users API failed: {e}")
        
        # Test 3: System status
        print("\n3. Testing System Status...")
        try:
            response = await client.get(f"{base_url}/admin/status")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"AI Available: {data.get('ai_available', False)}")
                print(f"Database Available: {data.get('database_available', False)}")
                print(f"LINE Configured: {data.get('line_configured', False)}")
                print(f"Telegram Configured: {data.get('telegram_configured', False)}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"System status failed: {e}")
        
        # Test 4: Create test user and test messages
        print("\n4. Testing Message History...")
        test_user_id = "test_admin_user_001"
        
        # First add some test data to database
        try:
            # This would be done through the actual bot interaction
            # For now, let's test with any existing user
            response = await client.get(f"{base_url}/admin/messages/{test_user_id}")
            print(f"Messages API Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Messages found: {len(data.get('messages', []))}")
                for msg in data.get('messages', [])[:3]:  # Show first 3 messages
                    print(f"  - {msg.get('sender_type', 'unknown')}: {msg.get('message', 'No message')[:50]}...")
            else:
                print(f"Messages error: {response.text}")
        except Exception as e:
            print(f"Messages API failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_admin_endpoints())
