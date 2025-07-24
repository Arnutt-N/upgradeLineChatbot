#!/usr/bin/env python3
"""
Test webhook functionality for LINE Bot
"""
import sys
import json
import httpx
import asyncio

# Add current directory to Python path
sys.path.insert(0, '.')

async def test_webhook():
    print("Testing webhook endpoints...")
    
    # Test 1: Health check
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/webhook")
            print(f"GET /webhook status: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.json()}")
    except Exception as e:
        print(f"GET /webhook error: {e}")
    
    # Test 2: Try a mock LINE webhook message
    try:
        # Create a mock LINE webhook event
        mock_event = {
            "events": [
                {
                    "type": "message",
                    "replyToken": "test-reply-token-12345",
                    "source": {
                        "userId": "U1234567890123456789012345678901a",
                        "type": "user"
                    },
                    "message": {
                        "id": "test-message-id-12345",
                        "type": "text",
                        "text": "สวัสดี ทดสอบบอท"
                    },
                    "timestamp": 1234567890123
                }
            ]
        }
        
        # Note: We cannot actually test this without proper LINE signature
        # But we can check if the endpoint exists
        print("Mock webhook event created (signature validation will fail but endpoint should exist)")
        print(f"Mock message: {mock_event['events'][0]['message']['text']}")
        
    except Exception as e:
        print(f"Mock webhook error: {e}")
    
    # Test 3: Check if Gemini service is working separately
    try:
        from app.services.gemini_service import GeminiService
        service = GeminiService()
        
        if service.is_available():
            print("Testing Gemini service directly...")
            result = await service.generate_response("สวัสดี", "test_user", use_session=False)
            print(f"Gemini test result: {result.get('success', False)}")
            if result.get('success'):
                print(f"Gemini response: {result.get('response', 'No response')[:100]}")
        else:
            print("Gemini service not available")
            
    except Exception as e:
        print(f"Gemini test error: {e}")
        
    # Test 4: Check LINE credentials
    try:
        from app.core.config import settings
        print(f"LINE Channel Secret: {'✓' if settings.LINE_CHANNEL_SECRET else '✗'}")
        print(f"LINE Access Token: {'✓' if settings.LINE_CHANNEL_ACCESS_TOKEN else '✗'}")
        print(f"Gemini API Key: {'✓' if settings.GEMINI_API_KEY else '✗'}")
        
    except Exception as e:
        print(f"Config check error: {e}")

if __name__ == "__main__":
    asyncio.run(test_webhook())