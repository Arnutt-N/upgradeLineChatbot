#!/usr/bin/env python3
"""
Diagnose admin panel and bot response issues
"""
import asyncio
import sys
import httpx

# Add current directory to Python path
sys.path.insert(0, '.')

async def diagnose_admin_panel():
    print("=== ADMIN PANEL DIAGNOSIS ===")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test 1: Check users endpoint
            response = await client.get('http://localhost:8000/admin/users')
            print(f"Admin Users API: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('users', [])
                print(f"Real users found: {len(users)}")
                
                if users:
                    user = users[0]
                    print(f"Sample user: {user.get('display_name', 'Unknown')}")
                    print(f"Latest message: {user.get('latest_message', 'None')[:50]}")
                    
                    # Test messages for first user
                    user_id = user['user_id']
                    msg_response = await client.get(f'http://localhost:8000/admin/messages/{user_id}')
                    print(f"Messages API: {msg_response.status_code}")
                    
                    if msg_response.status_code == 200:
                        msg_data = msg_response.json()
                        messages = msg_data.get('messages', [])
                        print(f"Messages for user: {len(messages)}")
                        
                        if messages:
                            print("Recent messages:")
                            for msg in messages[-3:]:  # Last 3 messages
                                sender = msg.get('sender_type', 'unknown')
                                content = msg.get('message', 'No content')[:30]
                                print(f"  {sender}: {content}...")
                else:
                    print("No users found in database!")
            else:
                print(f"API Error: {response.text}")
                
    except Exception as e:
        print(f"Admin panel test error: {e}")

async def diagnose_webhook():
    print("\n=== WEBHOOK DIAGNOSIS ===")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test webhook health
            response = await client.get('http://localhost:8000/webhook')
            print(f"Webhook health: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Webhook status: {data.get('status', 'unknown')}")
            
            # Check LINE configuration
            try:
                from app.core.config import settings
                print(f"LINE Channel Secret: {'SET' if settings.LINE_CHANNEL_SECRET else 'MISSING'}")
                print(f"LINE Access Token: {'SET' if settings.LINE_CHANNEL_ACCESS_TOKEN else 'MISSING'}")
                print(f"Gemini API Key: {'SET' if settings.GEMINI_API_KEY else 'MISSING'}")
                
                # Validate settings
                try:
                    settings.validate_required_settings()
                    print("LINE settings validation: PASSED")
                except Exception as e:
                    print(f"LINE settings validation: FAILED - {e}")
                    
            except Exception as e:
                print(f"Config check error: {e}")
                
    except Exception as e:
        print(f"Webhook test error: {e}")

async def diagnose_gemini():
    print("\n=== GEMINI BOT DIAGNOSIS ===")
    
    try:
        from app.services.gemini_service import GeminiService
        
        service = GeminiService()
        print(f"Gemini service available: {service.is_available()}")
        
        if service.is_available():
            # Test simple response
            result = await service.generate_response("สวัสดี", "test_user", use_session=False)
            print(f"Gemini test success: {result.get('success', False)}")
            
            if result.get('success'):
                response = result.get('response', '')
                print(f"Sample response: {response[:50]}...")
            else:
                print(f"Gemini error: {result.get('error', 'Unknown')}")
        else:
            print("Gemini service not available")
            
    except Exception as e:
        print(f"Gemini test error: {e}")

async def diagnose_database():
    print("\n=== DATABASE DIAGNOSIS ===")
    
    try:
        from app.db.database import get_db
        from app.db.models import UserStatus, ChatHistory
        from sqlalchemy import select, func
        
        async for db in get_db():
            try:
                # Count users
                result = await db.execute(select(func.count(UserStatus.user_id)))
                user_count = result.scalar()
                print(f"Total users in database: {user_count}")
                
                # Count messages
                result = await db.execute(select(func.count(ChatHistory.id)))
                message_count = result.scalar()
                print(f"Total messages in database: {message_count}")
                
                # Get recent messages
                result = await db.execute(
                    select(ChatHistory)
                    .order_by(ChatHistory.timestamp.desc())
                    .limit(3)
                )
                recent_messages = result.scalars().all()
                
                print(f"Recent messages:")
                for msg in recent_messages:
                    print(f"  {msg.message_type}: {msg.message_content[:30]}...")
                    
                break
                
            except Exception as e:
                print(f"Database query error: {e}")
                break
                
    except Exception as e:
        print(f"Database test error: {e}")

async def main():
    print("HR LINE CHATBOT DIAGNOSIS")
    print("=" * 50)
    
    await diagnose_database()
    await diagnose_admin_panel() 
    await diagnose_webhook()
    await diagnose_gemini()
    
    print("\n=== RECOMMENDATIONS ===")
    print("1. Check if admin panel browser cache needs clearing")
    print("2. Verify LINE webhook URL is set correctly in LINE Developer Console")
    print("3. Test sending a real LINE message to see webhook logs")
    print("4. Check server logs for any webhook events")

if __name__ == "__main__":
    asyncio.run(main())