# app/db/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from app.db.models import UserStatus, ChatMessage
import uuid

async def get_or_create_user_status(db: AsyncSession, user_id: str, display_name: str = None, picture_url: str = None) -> UserStatus:
    """รับหรือสร้างสถานะผู้ใช้ พร้อมอัปเดตชื่อผู้ใช้และรูปโปรไฟล์"""
    result = await db.execute(select(UserStatus).filter(UserStatus.user_id == user_id))
    user_status = result.scalar_one_or_none()
    
    if not user_status:
        # สร้างผู้ใช้ใหม่
        fallback_name = f"Customer {user_id[-6:]}"
        user_status = UserStatus(
            user_id=user_id, 
            display_name=display_name or fallback_name,
            picture_url=picture_url,
            is_in_live_chat=False, 
            chat_mode='manual'
        )
        db.add(user_status)
        await db.commit()
        await db.refresh(user_status)
        print(f"✅ Created new user: {user_id} with name: {user_status.display_name} (pic: {picture_url})")
    else:
        # อัปเดตชื่อผู้ใช้ถ้ามีการส่งมา และยังไม่มีชื่อจริง
        updated = False
        if display_name and (not user_status.display_name or user_status.display_name.startswith("Customer ")):
            user_status.display_name = display_name
            updated = True
        
        # อัปเดต picture_url ถ้ามีการส่งมา หรือยังไม่มี
        if picture_url and not user_status.picture_url:
            user_status.picture_url = picture_url
            updated = True
        
        if updated:
            await db.commit()
            print(f"✅ Updated user: {user_id} -> name: {display_name}, pic: {picture_url}")
    
    return user_status

async def set_live_chat_status(db: AsyncSession, user_id: str, status: bool, display_name: str = None, picture_url: str = None) -> UserStatus:
    """ตั้งค่าสถานะ live chat ของผู้ใช้"""
    user_status = await get_or_create_user_status(db, user_id, display_name, picture_url)
    user_status.is_in_live_chat = status
    await db.commit()
    return user_status

async def set_chat_mode(db: AsyncSession, user_id: str, mode: str, display_name: str = None, picture_url: str = None) -> UserStatus:
    """ตั้งค่าโหมดการแชทของผู้ใช้"""
    user_status = await get_or_create_user_status(db, user_id, display_name, picture_url)
    user_status.chat_mode = mode
    await db.commit()
    return user_status

async def save_chat_message(db: AsyncSession, user_id: str, sender_type: str, message: str) -> ChatMessage:
    """บันทึกข้อความแชท"""
    new_message = ChatMessage(
        id=str(uuid.uuid4()),
        user_id=user_id, 
        sender_type=sender_type, 
        message=message
    )
    db.add(new_message)
    await db.commit()
    return new_message

async def get_chat_messages(db: AsyncSession, user_id: str, limit: int = 100):
    """โหลดข้อความแชทของผู้ใช้"""
    result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    return result.scalars().all()

async def get_users_with_messages(db: AsyncSession):
    """โหลดรายการผู้ใช้ที่มีประวัติแชท พร้อมชื่อผู้ใช้และรูปโปรไฟล์"""
    result = await db.execute(
        select(UserStatus.user_id, UserStatus.display_name, UserStatus.picture_url, UserStatus.is_in_live_chat, UserStatus.chat_mode)
        .join(ChatMessage, UserStatus.user_id == ChatMessage.user_id)
        .distinct()
    )
    return result.all()

async def get_latest_message(db: AsyncSession, user_id: str):
    """โหลดข้อความล่าสุดของผู้ใช้"""
    result = await db.execute(
        select(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .order_by(desc(ChatMessage.created_at))
        .limit(1)
    )
    return result.scalar_one_or_none()
