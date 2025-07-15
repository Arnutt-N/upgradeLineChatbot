#!/usr/bin/env python3
"""
Test script to validate the fixes for the LINE Bot issues.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

async def test_gemini_service():
    """Test if Gemini service is working"""
    print("🧪 Testing Gemini Service...")
    
    try:
        from app.services.gemini_service import gemini_service, check_gemini_availability
        
        # Test availability
        is_available = await check_gemini_availability()
        print(f"✅ Gemini available: {is_available}")
        
        if is_available:
            # Test response generation
            result = await gemini_service.generate_response(
                user_message="สวัสดีครับ",
                user_id="test_user_123"
            )
            print(f"✅ Gemini response: {result['success']}")
            if result['success']:
                print(f"📝 Response: {result['response'][:100]}...")
            else:
                print(f"❌ Error: {result.get('error')}")
        
        return True
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

async def test_database_connection():
    """Test database connectivity"""
    print("🧪 Testing Database Connection...")
    
    try:
        from app.db.database import get_db
        from app.db.crud_enhanced import get_users_with_history
        
        # Get a database session
        async for db in get_db():
            try:
                users = await get_users_with_history(db)
                print(f"✅ Database connected, found {len(users)} users")
                return True
            except Exception as e:
                print(f"❌ Database query failed: {e}")
                return False
            finally:
                await db.close()
                
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_websocket_manager():
    """Test WebSocket manager"""
    print("🧪 Testing WebSocket Manager...")
    
    try:
        from app.services.ws_manager import manager
        
        # Test broadcast functionality (should not fail even with no connections)
        await manager.broadcast({
            "type": "test_message",
            "message": "Test broadcast",
            "timestamp": "2023-01-01T00:00:00"
        })
        print("✅ WebSocket manager working")
        return True
        
    except Exception as e:
        print(f"❌ WebSocket manager test failed: {e}")
        return False

async def test_enhanced_handlers():
    """Test if enhanced handlers can be imported"""
    print("🧪 Testing Enhanced Handlers...")
    
    try:
        from app.services.line_handler_enhanced import (
            handle_message_enhanced,
            handle_image_message_enhanced, 
            handle_file_message_enhanced,
            handle_follow_event,
            handle_unfollow_event
        )
        print("✅ Enhanced handlers imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced handlers import failed: {e}")
        return False

async def test_webhook_imports():
    """Test if webhook can import all required functions"""
    print("🧪 Testing Webhook Imports...")
    
    try:
        from app.api.routers.webhook import line_webhook
        print("✅ Webhook imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Webhook import failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Fix Validation Tests...")
    print("=" * 50)
    
    tests = [
        test_enhanced_handlers,
        test_webhook_imports,
        test_websocket_manager,
        test_gemini_service,
        test_database_connection,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = await test()
            if result:
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The fixes should be working.")
    else:
        print("⚠️  Some tests failed. There may be issues that need attention.")
        
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)