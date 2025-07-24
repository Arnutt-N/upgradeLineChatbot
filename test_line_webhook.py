#!/usr/bin/env python3
"""
Test LINE webhook with simulated message
"""
import asyncio
import sys
import json
import httpx
import hashlib
import hmac
import base64

# Add current directory to Python path
sys.path.insert(0, '.')

async def test_line_webhook():
    print("Testing LINE webhook with simulated message...")
    
    try:
        from app.core.config import settings
        
        # Create a mock LINE message event with all required fields
        webhook_body = {
            "events": [
                {
                    "type": "message",
                    "mode": "active",
                    "timestamp": 1708483200000,
                    "source": {
                        "type": "user",
                        "userId": "U1234567890123456789012345678901a"  # Our test user
                    },
                    "webhookEventId": "01FZ74A0TDDPYRVKNK77XKC3ZR",
                    "deliveryContext": {
                        "isRedelivery": False
                    },
                    "message": {
                        "id": "test-message-id-67890",
                        "type": "text", 
                        "text": "สวัสดี ทดสอบบอทตอบกลับ",
                        "quoteToken": "test-quote-token"
                    },
                    "replyToken": "test-reply-token-12345"
                }
            ],
            "destination": "test-destination"
        }
        
        # Convert to JSON string
        body_str = json.dumps(webhook_body)
        print(f"Webhook body: {body_str}")
        
        # Create LINE signature (like real LINE would do)
        channel_secret = settings.LINE_CHANNEL_SECRET
        if channel_secret:
            signature = base64.b64encode(
                hmac.new(
                    channel_secret.encode('utf-8'),
                    body_str.encode('utf-8'),
                    hashlib.sha256
                ).digest()
            ).decode()
            
            print(f"Generated signature: {signature}")
            
            # Send to webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    'http://localhost:8000/webhook',
                    content=body_str,
                    headers={
                        'Content-Type': 'application/json',
                        'X-Line-Signature': signature
                    }
                )
                
                print(f"Webhook response: {response.status_code}")
                print(f"Response body: {response.text}")
                
                if response.status_code == 200:
                    print("SUCCESS: Webhook accepted the message!")
                    print("Check server logs for bot response processing...")
                else:
                    print(f"ERROR: Webhook returned {response.status_code}")
        else:
            print("ERROR: No LINE channel secret configured")
            
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_line_webhook())