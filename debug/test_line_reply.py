import asyncio
import os
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhook import WebhookHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_reply():
    """Test LINE reply functionality"""
    
    # Get credentials
    channel_secret = os.getenv("LINE_CHANNEL_SECRET")
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    
    print(f"Channel Secret: {'Set' if channel_secret else 'NOT SET'}")
    print(f"Access Token: {'Set' if channel_access_token else 'NOT SET'}")
    
    if not channel_access_token:
        print("ERROR: LINE_CHANNEL_ACCESS_TOKEN not found!")
        return
    
    # Initialize API
    api = AsyncMessagingApi(channel_access_token)
    
    # Test token validation
    try:
        # This is a dummy reply token for testing
        test_message = TextMessage(text="Test message from debug script")
        
        print(f"\nAPI Client initialized successfully")
        print(f"Token length: {len(channel_access_token)}")
        
        # Note: To actually test reply, you need a valid reply token from a real webhook event
        print("\nTo test actual reply:")
        print("1. Send a message to your LINE bot")
        print("2. Check Render logs for the reply token")
        print("3. Use that token to test reply functionality")
        
    except Exception as e:
        print(f"Error initializing API: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_reply())
