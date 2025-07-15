#!/usr/bin/env python3
"""
Test Enhanced System Functions
ทดสอบฟังก์ชันใหม่ที่พัฒนา
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import get_db
from app.db.crud_enhanced import (
    save_chat_history, save_friend_activity, create_telegram_notification,
    log_system_event, get_chat_statistics, get_friend_statistics
)
from app.services.telegram_service import telegram_service
from app.services.history_service import history_service

async def test_enhanced_functions():
    """ทดสอบฟังก์ชันต่างๆ"""
    
    print("Testing Enhanced System Functions...")
    print("=" * 50)
    
    # Get database session
    async for db in get_db():
        try:
            # 1. Test Chat History
            print("1. Testing Chat History...")
            chat_record = await save_chat_history(
                db=db,
                user_id="test_user_001",
                message_type="user",
                message_content="สวัสดีค่ะ ทดสอบระบบใหม่",
                session_id="test_session_001",
                metadata={"test": True, "source": "test_script"}
            )
            print(f"   ✓ Chat history saved: {chat_record.id}")
            
            # 2. Test Friend Activity
            print("2. Testing Friend Activity...")
            friend_record = await save_friend_activity(
                db=db,
                user_id="test_user_001",
                activity_type="follow",
                user_profile={"display_name": "Test User", "source": "test"},
                source="test_script"
            )
            print(f"   ✓ Friend activity saved: {friend_record.id}")
            
            # 3. Test Telegram Notification
            print("3. Testing Telegram Notification...")
            telegram_record = await create_telegram_notification(
                db=db,
                notification_type="system_alert",
                title="ทดสอบระบบ",
                message="การทดสอบฟังก์ชันใหม่ทำงานสำเร็จ",
                priority=1,
                data={"test": True, "timestamp": "2025-07-13"}
            )
            print(f"   ✓ Telegram notification created: {telegram_record.id}")
            
            # 4. Test System Logging
            print("4. Testing System Logging...")
            log_record = await log_system_event(
                db=db,
                level="info",
                category="test",
                subcategory="function_test",
                message="Enhanced functions test completed successfully",
                details={"test_results": "all_passed"}
            )
            print(f"   ✓ System log saved: {log_record.id}")
            
            # 5. Test Statistics
            print("5. Testing Statistics...")
            chat_stats = await get_chat_statistics(db, days=1)
            friend_stats = await get_friend_statistics(db, days=1)
            print(f"   ✓ Chat stats: {chat_stats}")
            print(f"   ✓ Friend stats: {friend_stats}")
            
            # 6. Test History Service
            print("6. Testing History Service...")
            overview = await history_service.get_chat_overview(db, days=1)
            print(f"   ✓ History overview: {overview}")
            
            # 7. Test Telegram Service (config check only)
            print("7. Testing Telegram Service...")
            is_configured = await telegram_service.is_configured()
            print(f"   ✓ Telegram configured: {is_configured}")
            
            print("\n" + "=" * 50)
            print("✅ All tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(test_enhanced_functions())
