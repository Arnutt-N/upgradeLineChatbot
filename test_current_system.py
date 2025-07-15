#!/usr/bin/env python3
"""
Direct test of current system to see what's actually working
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

async def test_webhook_handler():
    """Test if webhook can handle a mock LINE event"""
    print("Testing webhook message handler...")
    
    try:
        from app.services.line_handler_enhanced import handle_message_enhanced
        from app.db.database import get_db
        from linebot.v3.messaging import AsyncMessagingApi, Configuration, AsyncApiClient
        from app.core.config import settings
        
        # Create mock event
        class MockMessage:
            def __init__(self):
                self.text = "Hello test"
                self.id = "test_message_123"
        
        class MockSource:
            def __init__(self):
                self.user_id = "U123456789test"
        
        class MockEvent:
            def __init__(self):
                self.source = MockSource()
                self.reply_token = "test_reply_token"
                self.message = MockMessage()
        
        # Create LINE API
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        line_bot_api = AsyncMessagingApi(async_api_client)
        
        # Test with database
        async for db in get_db():
            try:
                mock_event = MockEvent()
                print(f"Testing with mock event: user={mock_event.source.user_id}, message={mock_event.message.text}")
                
                # This should work if everything is connected properly
                await handle_message_enhanced(mock_event, db, line_bot_api)
                print("SUCCESS: Message handler completed without errors")
                
            except Exception as e:
                print(f"ERROR in message handler: {e}")
                import traceback
                traceback.print_exc()
            finally:
                await db.close()
                break
                
    except ImportError as e:
        print(f"IMPORT ERROR: {e}")
    except Exception as e:
        print(f"GENERAL ERROR: {e}")

async def test_gemini_response():
    """Test if Gemini is actually responding"""
    print("\nTesting Gemini AI response...")
    
    try:
        from app.services.gemini_service import gemini_service
        
        # Test simple response
        result = await gemini_service.generate_response(
            user_message="สวัสดีครับ",
            user_id="test_user_123"
        )
        
        print(f"Gemini available: {gemini_service.is_available()}")
        print(f"Response success: {result.get('success')}")
        
        if result.get('success'):
            print(f"Response preview: {result['response'][:100]}...")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"GEMINI ERROR: {e}")

async def test_websocket_broadcast():
    """Test WebSocket broadcasting"""
    print("\nTesting WebSocket broadcast...")
    
    try:
        from app.services.ws_manager import manager
        
        # Test broadcast (should work even with no connections)
        test_data = {
            "type": "test_message",
            "userId": "test123",
            "message": "Test broadcast",
            "timestamp": "2023-01-01T00:00:00"
        }
        
        await manager.broadcast(test_data)
        print(f"SUCCESS: Broadcast completed")
        print(f"Active connections: {len(manager.active_connections)}")
        
    except Exception as e:
        print(f"WEBSOCKET ERROR: {e}")

async def test_loading_animation():
    """Test loading animation API"""
    print("\nTesting LINE loading animation...")
    
    try:
        from app.services.line_handler_enhanced import show_loading_animation
        from linebot.v3.messaging import AsyncMessagingApi, Configuration, AsyncApiClient
        from app.core.config import settings
        
        # Create LINE API
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        line_bot_api = AsyncMessagingApi(async_api_client)
        
        # Test with fake user ID (should show API call attempt)
        result = await show_loading_animation(line_bot_api, "U123456789test", 3)
        print(f"Loading animation result: {result}")
        
    except Exception as e:
        print(f"LOADING ANIMATION ERROR: {e}")

async def main():
    print("=== TESTING CURRENT SYSTEM ===")
    print()
    
    await test_gemini_response()
    await test_websocket_broadcast() 
    await test_loading_animation()
    await test_webhook_handler()
    
    print()
    print("=== TEST COMPLETED ===")

if __name__ == "__main__":
    asyncio.run(main())