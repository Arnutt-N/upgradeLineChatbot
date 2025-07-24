#!/usr/bin/env python3
"""
Create test data for HR Project LINE Chatbot
"""
import asyncio
import sys
import uuid
from datetime import datetime, timedelta

# Add current directory to Python path
sys.path.insert(0, '.')

async def create_test_data():
    from app.db.database import get_db
    from app.db.models import UserStatus, ChatHistory
    from app.utils.timezone import get_thai_time
    
    print("Creating test data for HR Project LINE Chatbot...")
    
    async for db in get_db():
        try:
            # Thai timezone
            thai_time = get_thai_time()
            
            # Create test users
            test_users = [
                {
                    "user_id": "U1234567890123456789012345678901a",
                    "display_name": "สมชาย ใจดี",
                    "picture_url": "/static/images/avatars/default_user_avatar.png",
                    "is_in_live_chat": True,
                    "chat_mode": "manual"
                },
                {
                    "user_id": "U1234567890123456789012345678901b", 
                    "display_name": "สมหญิง รักงาน",
                    "picture_url": "/static/images/avatars/default_user_avatar.png",
                    "is_in_live_chat": False,
                    "chat_mode": "auto"
                },
                {
                    "user_id": "U1234567890123456789012345678901c",
                    "display_name": "นายทดสอบ ระบบงาน", 
                    "picture_url": "/static/images/avatars/default_user_avatar.png",
                    "is_in_live_chat": False,
                    "chat_mode": "bot"
                }
            ]
            
            print("Creating test users...")
            for user_data in test_users:
                user = UserStatus(**user_data)
                db.add(user)
                print(f"  Created user: {user_data['display_name']}")
            
            await db.commit()
            print("Users created successfully!")
            
            # Create test chat history
            print("Creating test chat messages...")
            
            test_messages = [
                # Conversation 1 - สมชาย ใจดี
                {
                    "user_id": "U1234567890123456789012345678901a",
                    "message_type": "user",
                    "message_content": "สวัสดีครับ ผมอยากสอบถามเรื่องการลาป่วยครับ",
                    "timestamp": thai_time - timedelta(minutes=30)
                },
                {
                    "user_id": "U1234567890123456789012345678901a", 
                    "message_type": "admin",
                    "message_content": "สวัสดีค่ะ สามารถช่วยได้ค่ะ ต้องการสอบถามเรื่องอะไรเกี่ยวกับการลาป่วยคะ?",
                    "timestamp": thai_time - timedelta(minutes=29)
                },
                {
                    "user_id": "U1234567890123456789012345678901a",
                    "message_type": "user", 
                    "message_content": "ผมป่วยเป็นไข้หวัดครับ จะขอลา 2 วันได้ไหมครับ",
                    "timestamp": thai_time - timedelta(minutes=28)
                },
                {
                    "user_id": "U1234567890123456789012345678901a",
                    "message_type": "admin",
                    "message_content": "ได้เลยค่ะ กรุณาแนบใบรับรองแพทย์มาด้วยนะคะ และกรอกใบลาในระบบ HR ด้วยค่ะ",
                    "timestamp": thai_time - timedelta(minutes=27)
                },
                
                # Conversation 2 - สมหญิง รักงาน  
                {
                    "user_id": "U1234567890123456789012345678901b",
                    "message_type": "user",
                    "message_content": "สอบถามเวลาทำงานค่ะ",
                    "timestamp": thai_time - timedelta(minutes=15)
                },
                {
                    "user_id": "U1234567890123456789012345678901b",
                    "message_type": "ai_bot", 
                    "message_content": "สวัสดีค่ะ! เวลาทำงานของเราคือ วันจันทร์-ศุกร์ เวลา 08:00-17:00 น. ค่ะ หากมีคำถามเพิ่มเติม สามารถสอบถามได้เลยค่ะ",
                    "timestamp": thai_time - timedelta(minutes=14)
                },
                {
                    "user_id": "U1234567890123456789012345678901b",
                    "message_type": "user",
                    "message_content": "ขอบคุณค่ะ แล้วการลาก่อนกำหนดล่วงหน้าต้องทำอย่างไรคะ?",
                    "timestamp": thai_time - timedelta(minutes=13)  
                },
                {
                    "user_id": "U1234567890123456789012345678901b",
                    "message_type": "ai_bot",
                    "message_content": "สำหรับการลาล่วงหน้า กรุณาส่งใบลาอย่างน้อย 3 วันทำการก่อนวันที่ต้องการลาค่ะ และต้องได้รับการอนุมัติจากหัวหน้างานก่อนค่ะ",
                    "timestamp": thai_time - timedelta(minutes=12)
                },
                
                # Conversation 3 - นายทดสอบ ระบบงาน
                {
                    "user_id": "U1234567890123456789012345678901c",
                    "message_type": "user",
                    "message_content": "ทดสอบระบบครับ",
                    "timestamp": thai_time - timedelta(minutes=5)
                },
                {
                    "user_id": "U1234567890123456789012345678901c",
                    "message_type": "bot",
                    "message_content": "สวัสดีครับ! ระบบทำงานปกติ พร้อมให้บริการครับ มีอะไรให้ช่วยเหลือไหมครับ?",
                    "timestamp": thai_time - timedelta(minutes=4)
                }
            ]
            
            for msg_data in test_messages:
                chat_msg = ChatHistory(
                    id=str(uuid.uuid4()),
                    session_id=f"session_{msg_data['user_id']}_{thai_time.strftime('%Y%m%d')}",
                    **msg_data
                )
                db.add(chat_msg)
                print(f"  Added message from {msg_data['message_type']}: {msg_data['message_content'][:50]}...")
            
            await db.commit()
            print("Test messages created successfully!")
            
            # Summary
            print("")
            print("Test data creation completed!")
            print("Summary:")
            print(f"  Users created: {len(test_users)}")
            print(f"  Messages created: {len(test_messages)}")
            print("")
            print("You can now:")
            print("  1. Check the admin panel: http://localhost:8000/admin")
            print("  2. View users and their chat histories")
            print("  3. Test the live chat functionality")
            
            break
            
        except Exception as e:
            print(f"Error creating test data: {e}")
            import traceback
            traceback.print_exc()
            break

if __name__ == "__main__":
    asyncio.run(create_test_data())