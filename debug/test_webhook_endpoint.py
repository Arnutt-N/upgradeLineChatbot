# Simple test endpoint to verify LINE connection
from fastapi import APIRouter, Request
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
import os
import json

router = APIRouter()

@router.post("/test-webhook")
async def test_webhook(request: Request):
    """Test endpoint to debug LINE webhook"""
    
    body = await request.body()
    data = json.loads(body)
    
    print("=== TEST WEBHOOK RECEIVED ===")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    # Get the first event
    if data.get("events"):
        event = data["events"][0]
        reply_token = event.get("replyToken")
        
        if reply_token:
            try:
                # Initialize LINE API
                token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
                api = AsyncMessagingApi(token)
                
                # Send reply
                await api.reply_message(
                    ReplyMessageRequest(
                        replyToken=reply_token,
                        messages=[TextMessage(text="Test reply from debug endpoint")]
                    )
                )
                print("✅ Test reply sent successfully!")
                
            except Exception as e:
                print(f"❌ Error sending test reply: {str(e)}")
    
    return {"status": "ok"}
