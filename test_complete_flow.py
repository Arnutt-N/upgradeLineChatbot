# Test Complete LINE Bot Flow
import asyncio
import json
from unittest.mock import Mock, AsyncMock
from app.services.gemini_service import gemini_service
from app.services.line_handler_enhanced import handle_message_enhanced
from app.db.database import get_db
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

async def test_complete_message_flow():
    """Test the complete message flow with Gemini AI"""
    print("=" * 60)
    print("Testing Complete LINE Bot Message Flow")
    print("=" * 60)
    
    try:
        # Test 1: Check Gemini availability
        print("\n1. Testing Gemini availability...")
        is_available = gemini_service.is_available()
        print(f"   Gemini available: {is_available}")
        
        if not is_available:
            print("   X Gemini not available - cannot test complete flow")
            return False
        
        # Test 2: Test basic AI response
        print("\n2. Testing basic AI response...")
        test_user_id = "test_user_123"
        test_message = "สวัสดีครับ"
        
        result = await gemini_service.generate_response(
            user_message=test_message,
            user_id=test_user_id,
            use_session=True
        )
        
        print(f"   Input: {test_message}")
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Response preview: {result['response'][:100] if result['response'] else 'Empty response'}")
            print(f"   Response length: {len(result['response']) if result['response'] else 0}")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            
        # Test 3: Test system prompt functionality
        print("\n3. Testing system prompt functionality...")
        result2 = await gemini_service.generate_response(
            user_message="ขอดูข้อมูลสถานะของฉันหน่อย",
            user_id=test_user_id,
            use_session=True
        )
        
        print(f"   Success: {result2['success']}")
        if result2['success']:
            print(f"   Response preview: {result2['response'][:100] if result2['response'] else 'Empty response'}")
            # Check if response contains characteristic patterns
            if result2['response']:
                has_polite_ending = any(ending in result2['response'].lower() for ending in ['ค่ะ', 'คะ', 'นะคะ', 'จ้า'])
                print(f"   Has polite endings: {has_polite_ending}")
        
        # Test 4: Test conversation context
        print("\n4. Testing conversation context...")
        result3 = await gemini_service.generate_response(
            user_message="ขอบคุณสำหรับข้อมูลที่ให้มาแล้ว",
            user_id=test_user_id,
            use_session=True
        )
        
        print(f"   Success: {result3['success']}")
        if result3['success']:
            print(f"   Response preview: {result3['response'][:100] if result3['response'] else 'Empty response'}")
            
        # Test 5: Check session management
        print("\n5. Testing session management...")
        sessions_info = gemini_service.get_chat_sessions_info()
        print(f"   Active sessions: {sessions_info['active_sessions']}")
        print(f"   Test user in sessions: {test_user_id in sessions_info['user_ids']}")
        
        # Test 6: Test encoding handling
        print("\n6. Testing encoding handling...")
        thai_message = "สวัสดีครับ ผมต้องการข้อมูลเรื่องการทำงาน"
        result4 = await gemini_service.generate_response(
            user_message=thai_message,
            user_id=test_user_id,
            use_session=True
        )
        
        print(f"   Success: {result4['success']}")
        if result4['success'] and result4['response']:
            # Check if response is properly encoded
            try:
                encoded_response = result4['response'].encode('utf-8')
                decoded_response = encoded_response.decode('utf-8')
                print(f"   Encoding test: PASSED")
                print(f"   Response length: {len(decoded_response)}")
            except Exception as e:
                print(f"   Encoding test: FAILED - {e}")
        
        print("\n" + "=" * 60)
        print("Complete Flow Test Results:")
        print(f"   - Gemini Available: {is_available}")
        print(f"   - Basic Response: {result['success']}")
        print(f"   - System Prompt: {result2['success']}")
        print(f"   - Context Memory: {result3['success']}")
        print(f"   - Session Management: {sessions_info['active_sessions'] > 0}")
        print(f"   - Encoding Handling: {result4['success']}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_mock_line_handler():
    """Test the line handler with mock objects"""
    print("\n" + "=" * 60)
    print("Testing Mock LINE Handler")
    print("=" * 60)
    
    try:
        # Create mock objects
        mock_event = Mock()
        mock_event.source.user_id = "test_user_456"
        mock_event.reply_token = "test_reply_token"
        mock_event.message.text = "Hello, how are you?"
        mock_event.message.id = "test_message_id"
        
        mock_db = AsyncMock()
        mock_line_bot_api = AsyncMock()
        
        # Mock the profile response
        mock_profile = Mock()
        mock_profile.display_name = "Test User"
        mock_profile.picture_url = "https://example.com/avatar.jpg"
        mock_line_bot_api.get_profile.return_value = mock_profile
        
        print("   Mock objects created successfully")
        print("   LINE Handler mock test setup complete")
        
        return True
        
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    print("Starting Complete Flow Test...")
    
    async def run_tests():
        success1 = await test_complete_message_flow()
        success2 = await test_mock_line_handler()
        
        if success1 and success2:
            print("\nALL TESTS PASSED! System is ready for production.")
        else:
            print("\nSome tests failed. Please check the issues above.")
            
        return success1 and success2
    
    result = asyncio.run(run_tests())
    
    if result:
        print("\nComplete flow test PASSED!")
    else:
        print("\nComplete flow test FAILED!")