# Test Bot Response
import asyncio
from unittest.mock import Mock, AsyncMock
from app.services.line_handler_enhanced import handle_message_enhanced
from app.db.database import get_db
from app.db.crud import get_or_create_user_status
from linebot.v3.messaging import AsyncMessagingApi

async def test_bot_response():
    """Test if bot responds to messages"""
    print("Testing bot response...")
    
    # Get database session
    async for db in get_db():
        try:
            user_id = "U693cb72c4dff8525756775d5fce45296"
            
            # Check current user status
            user_status = await get_or_create_user_status(
                db, user_id, "Arnutt Topp", None
            )
            
            print(f"User status:")
            print(f"  - Is in live chat: {user_status.is_in_live_chat}")
            print(f"  - Chat mode: {user_status.chat_mode}")
            
            # Create mock objects for testing
            mock_event = Mock()
            mock_event.source.user_id = user_id
            mock_event.reply_token = "test_reply_token"
            mock_event.message.text = "สวัสดี"
            mock_event.message.id = "test_message_id"
            
            mock_line_bot_api = AsyncMock()
            mock_profile = Mock()
            mock_profile.display_name = "Arnutt Topp"
            mock_profile.picture_url = "https://example.com/avatar.jpg"
            mock_line_bot_api.get_profile.return_value = mock_profile
            
            print("\nTesting message handler...")
            
            # This should trigger bot response based on the current mode
            if user_status.is_in_live_chat and user_status.chat_mode == 'auto':
                print("Expected behavior: Bot should respond (live chat + auto mode)")
            elif not user_status.is_in_live_chat:
                print("Expected behavior: Bot should respond (bot mode)")
            else:
                print("Expected behavior: Bot should NOT respond (live chat + manual mode)")
                
            print("Bot response test setup complete!")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(test_bot_response())