#!/usr/bin/env python3
"""
Test bot response flow without going through webhook
"""
import sys
import asyncio

# Add current directory to Python path
sys.path.insert(0, '.')

async def test_bot_flow():
    print("Testing bot response flow...")
    
    try:
        from app.db.database import get_db
        from app.services.line_handler_enhanced import handle_bot_mode_message
        from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration
        from app.core.config import settings
        
        # Create LINE API client
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        line_bot_api = AsyncMessagingApi(async_api_client)
        
        # Test user from our database
        test_user_id = "U1234567890123456789012345678901a"
        test_message = "สวัสดี ทดสอบระบบ"
        test_reply_token = "test-reply-token-12345"
        
        # Mock profile data
        profile_data = {
            "user_id": test_user_id,
            "display_name": "สมชาย ใจดี",
            "picture_url": "/static/images/avatars/default_user_avatar.png"
        }
        
        # Get database session
        async for db in get_db():
            print(f"Testing bot response for user: {profile_data['display_name']}")
            print(f"Message: {test_message}")
            
            try:
                # Test the bot mode message handler
                await handle_bot_mode_message(
                    db=db,
                    line_bot_api=line_bot_api,
                    user_id=test_user_id,
                    message_text=test_message,
                    reply_token=test_reply_token,
                    profile_data=profile_data,
                    session_id=f"test_session_{test_user_id}"
                )
                
                print("Bot response test completed successfully!")
                
            except Exception as e:
                print(f"Bot response error: {e}")
                import traceback
                traceback.print_exc()
            
            break
            
    except Exception as e:
        print(f"Setup error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bot_flow())