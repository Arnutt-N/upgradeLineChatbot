: Database connection and models
    try:
        from app.db.database import get_db, create_db_and_tables
        from app.db.crud_enhanced import (
            save_chat_to_history, 
            get_all_chat_history_by_user,
            get_users_with_history,
            get_latest_chat_in_history
        )
        from app.db.models import Base
        
        print("✅ Successfully imported database modules")
        
        # Test database connection
        await create_db_and_tables()
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    # Test 2: CRUD operations
    try:
        from app.db.database import async_session
        
        async with async_session() as db:
            # Test saving chat message
            test_chat = await save_chat_to_history(
                db=db,
                user_id="test_admin_001",
                message_type="user", 
                message_content="Test message for admin panel"
            )
            print(f"✅ Chat save test: ID {test_chat.id}")
            
            # Test retrieving messages
            messages = await get_all_chat_history_by_user(db, "test_admin_001")
            print(f"✅ Message retrieval test: Found {len(messages)} messages")
            
            # Test getting users
            users = await get_users_with_history(db)
            print(f"✅ Users list test: Found {len(users)} users")
            
            # Clean up test data
            await db.execute(
                text("DELETE FROM chat_history WHERE user_id = 'test_admin_001'")
            )
            await db.commit()
            print("✅ Test data cleaned up")
            
    except Exception as e:
        print(f"❌ CRUD operations test failed: {e}")
        return False
    
    # Test 3: API endpoints simulation
    try:
        from app.api.routers.admin import get_users_list, get_user_messages
        from app.core.config import settings
        
        print("✅ Admin router functions imported")
        print(f"✅ Settings loaded - LINE configured: {bool(settings.LINE_CHANNEL_ACCESS_TOKEN)}")
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False
    
    # Test 4: WebSocket manager
    try:
        from app.services.ws_manager import manager
        print("✅ WebSocket manager imported")
        print(f"✅ Active connections: {len(manager.active_connections)}")
        
    except Exception as e:
        print(f"❌ WebSocket manager test failed: {e}")
        return False
    
    # Test 5: Gemini service
    try:
        from app.services.gemini_service import GeminiService, check_gemini_availability
        
        # Test if Gemini is available
        is_available = await check_gemini_availability()
        print(f"✅ Gemini service available: {is_available}")
        
        if is_available:
            # Test simple generation
            service = GeminiService()
            response = await service.get_ai_response("test_user", "สวัสดี")
            if response:
                print(f"✅ Gemini response test: {response[:50]}...")
            else:
                print("⚠️ Gemini response was empty")
        
    except Exception as e:
        print(f"❌ Gemini service test failed: {e}")
        return False
    
    # Test 6: LINE handler functions
    try:
        from app.services.line_handler_enhanced import show_loading_animation
        print("✅ LINE handler functions imported")
        
    except Exception as e:
        print(f"❌ LINE handler test failed: {e}")
        return False
    
    print("\n🎉 All admin panel function tests passed!")
    return True

if __name__ == "__main__":
    from sqlalchemy import text
    result = asyncio.run(test_admin_panel_functions())
    
    if result:
        print("\n✅ Admin Panel is ready to use!")
        print("Start the server with: python main.py")
        print("Access admin panel at: http://localhost:8000/admin")
    else:
        print("\n❌ Some tests failed - check the errors above")
