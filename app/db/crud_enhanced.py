# Enhanced CRUD operations for new tracking tables
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import (
    ChatHistory, FriendActivity, TelegramNotification, 
    TelegramSettings, SystemLogs, UserStatus  # <-- เพิ่ม UserStatus สำหรับ join
)

# ========================================
# Chat History CRUD (ปรับปรุงสำหรับ Admin Panel)
# ========================================

async def save_chat_to_history(
    db: AsyncSession,
    user_id: str,
    message_type: str,
    message_content: str,
    admin_user_id: Optional[str] = None,
    message_id: Optional[str] = None,
    reply_token: Optional[str] = None,
    session_id: Optional[str] = None,
    extra_data: Optional[Dict] = None
) -> ChatHistory:
    """
    (ชื่อเดิม save_chat_history)
    บันทึกประวัติการแชทแบบละเอียดลงในตาราง chat_history
    """
    chat_history = ChatHistory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        message_type=message_type,
        message_content=message_content,
        admin_user_id=admin_user_id,
        message_id=message_id,
        reply_token=reply_token,
        session_id=session_id or f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}",
        extra_data=json.dumps(extra_data) if extra_data else None
    )
    
    db.add(chat_history)
    await db.commit()
    await db.refresh(chat_history)
    return chat_history

async def get_all_chat_history_by_user(
    db: AsyncSession,
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[ChatHistory]:
    """
    (ฟังก์ชันใหม่ - แทนที่ get_chat_history)
    ดึงประวัติแชททั้งหมดของผู้ใช้คนเดียว เรียงจากเก่าไปใหม่สำหรับแสดงผลในห้องแชท
    """
    query = select(ChatHistory).where(
        ChatHistory.user_id == user_id
    ).order_by(
        ChatHistory.timestamp.asc()  # <-- แก้ไข: เรียงจากเก่าไปใหม่
    ).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_users_with_history(db: AsyncSession) -> List[UserStatus]:
    """
    (ฟังก์ชันใหม่)
    ดึงรายชื่อผู้ใช้ทั้งหมด (จาก UserStatus) - แสดงทุกคนไม่ว่าจะมีประวัติแชทหรือไม่
    """
    query = select(UserStatus).order_by(UserStatus.updated_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_latest_chat_in_history(db: AsyncSession, user_id: str) -> Optional[ChatHistory]:
    """
    (ฟังก์ชันใหม่)
    ดึงข้อความล่าสุดเพียง 1 ข้อความของผู้ใช้ เพื่อแสดงในหน้ารายชื่อ
    """
    query = select(ChatHistory).where(
        ChatHistory.user_id == user_id
    ).order_by(
        ChatHistory.timestamp.desc()
    ).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_chat_history(
    db: AsyncSession,
    user_id: Optional[str] = None,
    message_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[ChatHistory]:
    """
    ดึงประวัติการแชทแบบละเอียด พร้อมการกรองข้อมูล
    """
    query = select(ChatHistory)
    
    # Apply filters
    conditions = []
    if user_id:
        conditions.append(ChatHistory.user_id == user_id)
    if message_type:
        conditions.append(ChatHistory.message_type == message_type)
    if start_date:
        conditions.append(ChatHistory.timestamp >= start_date)
    if end_date:
        conditions.append(ChatHistory.timestamp <= end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(ChatHistory.timestamp.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()


async def mark_messages_as_read(
    db: AsyncSession,
    user_id: str
) -> int:
    """ทำเครื่องหมายข้อความว่าอ่านแล้ว"""
    query = select(ChatHistory).where(
        and_(
            ChatHistory.user_id == user_id,
            ChatHistory.is_read == False,
            ChatHistory.message_type == 'user'
        )
    )
    result = await db.execute(query)
    messages = result.scalars().all()
    
    count = 0
    for message in messages:
        message.is_read = True
        count += 1
    
    if count > 0:
        await db.commit()
    return count

# ========================================
# Friend Activity CRUD  
# ========================================

async def save_friend_activity(
    db: AsyncSession,
    user_id: str,
    activity_type: str,
    user_profile: Optional[Dict] = None,
    event_data: Optional[Dict] = None,
    source: str = 'line_webhook',
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> FriendActivity:
    """บันทึกประวัติการเพิ่ม/ลบเพื่อน"""
    activity = FriendActivity(
        id=str(uuid.uuid4()),
        user_id=user_id,
        activity_type=activity_type,
        user_profile=json.dumps(user_profile) if user_profile else None,
        event_data=json.dumps(event_data) if event_data else None,
        source=source,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(activity)
    await db.commit()
    await db.refresh(activity)
    return activity

async def get_friend_activities(
    db: AsyncSession,
    user_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[FriendActivity]:
    """ดึงประวัติกิจกรรมเพื่อน"""
    query = select(FriendActivity)
    if user_id:
        query = query.where(FriendActivity.user_id == user_id)
    if activity_type:
        query = query.where(FriendActivity.activity_type == activity_type)
    
    query = query.order_by(FriendActivity.timestamp.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

# ========================================
# Telegram Notification CRUD
# ========================================

async def create_telegram_notification(
    db: AsyncSession,
    notification_type: str,
    title: str,
    message: str,
    user_id: Optional[str] = None,
    priority: int = 1,
    extra_data: Optional[Dict] = None
) -> TelegramNotification:
    """สร้างการแจ้งเตือนไป Telegram"""
    notification = TelegramNotification(
        id=str(uuid.uuid4()),
        notification_type=notification_type,
        title=title,
        message=message,
        user_id=user_id,
        priority=priority,
        extra_data=json.dumps(extra_data) if extra_data else None,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification

async def get_pending_notifications(
    db: AsyncSession,
    limit: int = 10
) -> List[TelegramNotification]:
    """ดึงการแจ้งเตือนที่รอส่ง"""
    query = select(TelegramNotification).where(
        TelegramNotification.status == 'pending'
    ).order_by(
        TelegramNotification.priority.desc(),
        TelegramNotification.created_at.asc() # แก้ไขจาก timestamp เป็น created_at
    ).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_notification_status(
    db: AsyncSession,
    notification_id: str,
    status: str,
    telegram_message_id: Optional[int] = None,
    error_message: Optional[str] = None
) -> bool:
    """อัพเดทสถานะการแจ้งเตือน"""
    query = select(TelegramNotification).where(TelegramNotification.id == notification_id)
    result = await db.execute(query)
    notification = result.scalar_one_or_none()
    
    if notification:
        notification.status = status
        if telegram_message_id:
            notification.telegram_message_id = telegram_message_id
        if error_message:
            notification.error_message = error_message
        if status == 'sent':
            notification.sent_at = datetime.now()
        elif status == 'failed':
            notification.retry_count = (notification.retry_count or 0) + 1
        
        await db.commit()
        return True
    return False

# ========================================
# Telegram Settings CRUD
# ========================================

async def get_telegram_setting(db: AsyncSession, setting_key: str) -> Optional[str]:
    """ดึงค่า setting จาก key"""
    query = select(TelegramSettings.setting_value).where(
        TelegramSettings.setting_key == setting_key
    )
    result = await db.execute(query)
    setting = result.scalar_one_or_none()
    return setting

async def update_telegram_setting(
    db: AsyncSession, 
    setting_key: str, 
    setting_value: str,
    updated_by: Optional[str] = None
) -> bool:
    """อัพเดทค่า setting"""
    query = select(TelegramSettings).where(TelegramSettings.setting_key == setting_key)
    result = await db.execute(query)
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.setting_value = setting_value
        setting.updated_by = updated_by
        await db.commit()
        return True
    return False

# ========================================
# System Logs CRUD
# ========================================

async def log_system_event(
    db: AsyncSession,
    level: str,
    category: str,
    message: str,
    subcategory: Optional[str] = None,
    details: Optional[Dict] = None,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    execution_time: Optional[int] = None
):
    """บันทึก System Log Event"""
    log_entry = SystemLogs(
        id=str(uuid.uuid4()),
        log_level=level,
        category=category,
        subcategory=subcategory,
        message=message,
        details=json.dumps(details) if details else None,
        user_id=user_id,
        request_id=request_id,
        execution_time=execution_time
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)
    return log_entry

async def get_system_logs(
    db: AsyncSession,
    level: Optional[str] = None,
    category: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SystemLogs]:
    """ดึง System Logs"""
    query = select(SystemLogs)
    if level:
        query = query.where(SystemLogs.log_level == level)
    if category:
        query = query.where(SystemLogs.category == category)
    if user_id:
        query = query.where(SystemLogs.user_id == user_id)
    
    query = query.order_by(SystemLogs.timestamp.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
