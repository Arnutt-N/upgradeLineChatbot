# Enhanced LINE Handler with Comprehensive Tracking
import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest, PushMessageRequest, ShowLoadingAnimationRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent

from app.core.config import settings
from app.db.crud import get_or_create_user_status, set_live_chat_status, save_chat_message
from app.db.crud_enhanced import (
    save_chat_history, save_friend_activity, create_telegram_notification,
    log_system_event
)
from app.services.ws_manager import manager

# ========================================
# Enhanced User Profile Functions
# ========================================

async def get_user_profile_enhanced(line_bot_api: AsyncMessagingApi, user_id: str) -> Dict[str, Any]:
    """ดึงโปรไฟล์ผู้ใช้แบบละเอียด พร้อม error handling"""
    profile_data = {
        "user_id": user_id,
        "display_name": f"Customer {user_id[-6:]}",
        "picture_url": None,
        "status_message": None,
        "language": None,
        "source": "fallback"
    }
    
    try:
        print(f"Getting profile for user: {user_id}")
        
        # ลองใช้ LINE Bot SDK ก่อน
        profile = await line_bot_api.get_profile(user_id)
        if profile and hasattr(profile, 'display_name'):
            profile_data.update({
                "display_name": profile.display_name,
                "picture_url": getattr(profile, 'picture_url', None),
                "status_message": getattr(profile, 'status_message', None),
                "language": getattr(profile, 'language', None),
                "source": "line_sdk"
            })
            print(f"Profile from SDK: {profile_data['display_name']}")
            return profile_data
            
    except Exception as e:
        print(f"SDK failed: {e}")
        
    # ลองใช้ Direct API
    try:
        return await get_user_profile_direct_enhanced(user_id, profile_data)
    except Exception as e:
        print(f"Direct API failed: {e}")
        return profile_data

async def get_user_profile_direct_enhanced(user_id: str, fallback_data: Dict) -> Dict[str, Any]:
    """ดึงโปรไฟล์โดยใช้ httpx โดยตรง - enhanced version"""
    headers = {
        'Authorization': f'Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://api.line.me/v2/bot/profile/{user_id}',
            headers=headers,
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            fallback_data.update({
                "display_name": data.get('displayName', fallback_data['display_name']),
                "picture_url": data.get('pictureUrl', None),
                "status_message": data.get('statusMessage', None),
                "language": data.get('language', None),
                "source": "direct_api"
            })
            print(f"Profile from Direct API: {fallback_data['display_name']}")
        
        return fallback_data

# ========================================
# Enhanced Telegram Functions
# ========================================

async def send_telegram_notification_enhanced(
    db: AsyncSession,
    notification_type: str,
    title: str,
    message: str,
    user_id: Optional[str] = None,
    priority: int = 2,
    data: Optional[Dict] = None
) -> bool:
    """ส่งการแจ้งเตือนไป Telegram แบบละเอียด"""
    
    # สร้าง notification record ในฐานข้อมูลก่อน
    notification = await create_telegram_notification(
        db=db,
        notification_type=notification_type,
        title=title,
        message=message,
        user_id=user_id,
        priority=priority,
        data=data
    )
    
    # ลอง log ระบบ
    await log_system_event(
        db=db,
        level="info",
        category="telegram",
        subcategory="notification_created",
        message=f"Created notification: {notification_type}",
        details={"notification_id": notification.id, "user_id": user_id}
    )
    
    # ถ้าไม่มี Telegram config ให้ส่งแค่ log
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        await log_system_event(
            db=db,
            level="warning", 
            category="telegram",
            subcategory="config_missing",
            message="Telegram credentials not configured",
            details={"notification_id": notification.id}
        )
        return False
    
    # ส่งข้อความไป Telegram
    return await send_to_telegram_actual(db, notification.id, title, message, data)

async def send_to_telegram_actual(
    db: AsyncSession, 
    notification_id: str, 
    title: str, 
    message: str, 
    data: Optional[Dict]
) -> bool:
    """ส่งข้อความไป Telegram จริงๆ"""
    
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # สร้างข้อความ
    formatted_message = f"*{title}*\n\n{message}"
    if data and 'timestamp' in data:
        formatted_message += f"\n\n_เวลา: {data['timestamp']}_"
    
    params = {
        'chat_id': settings.TELEGRAM_CHAT_ID,
        'text': formatted_message,
        'parse_mode': 'Markdown'
    }
    
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            
            # อัพเดทสถานะเป็น sent
            from app.db.crud_enhanced import update_notification_status
            await update_notification_status(
                db=db,
                notification_id=notification_id,
                status='sent',
                telegram_message_id=response.json().get('result', {}).get('message_id')
            )
            
            await log_system_event(
                db=db,
                level="info",
                category="telegram", 
                subcategory="message_sent",
                message="Telegram message sent successfully",
                details={"notification_id": notification_id}
            )
            
            return True
            
    except Exception as e:
        # อัพเดทสถานะเป็น failed
        from app.db.crud_enhanced import update_notification_status
        await update_notification_status(
            db=db,
            notification_id=notification_id,
            status='failed',
            error_message=str(e)
        )
        
        await log_system_event(
            db=db,
            level="error",
            category="telegram",
            subcategory="send_failed", 
            message=f"Failed to send Telegram message: {str(e)}",
            details={"notification_id": notification_id, "error": str(e)}
        )
        
        return False

# ========================================
# Enhanced Event Handlers
# ========================================

async def handle_message_enhanced(
    event: MessageEvent, 
    db: AsyncSession, 
    line_bot_api: AsyncMessagingApi
):
    """จัดการข้อความ - Enhanced version with comprehensive tracking"""
    
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_text = event.message.text
    message_id = getattr(event.message, 'id', None)
    
    # สร้าง session ID สำหรับ tracking
    session_id = f"session_{user_id}_{datetime.now().strftime('%Y%m%d')}"
    
    print(f"Message from {user_id}: {message_text}")
    
    # ดึงโปรไฟล์ผู้ใช้แบบละเอียด
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    
    # บันทึกข้อความใน ChatHistory (ตารางใหม่)
    await save_chat_history(
        db=db,
        user_id=user_id,
        message_type='user',
        message_content=message_text,
        message_id=message_id,
        reply_token=reply_token,
        session_id=session_id,
        extra_data={
            "profile_data": profile_data,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # รับสถานะผู้ใช้ (ตารางเดิม - เพื่อ compatibility)
    user_status = await get_or_create_user_status(
        db, user_id, profile_data['display_name'], profile_data['picture_url']
    )
    
    # บันทึกใน chat_messages เดิมด้วย (เพื่อ backward compatibility)
    await save_chat_message(db, user_id, 'user', message_text)
    
    if user_status.is_in_live_chat:
        # Live Chat Mode
        await handle_live_chat_message(
            db, line_bot_api, user_id, message_text, reply_token, 
            user_status, profile_data, session_id
        )
    else:
        # Bot Mode
        await handle_bot_mode_message(
            db, line_bot_api, user_id, message_text, reply_token,
            profile_data, session_id
        )

async def handle_live_chat_message(
    db: AsyncSession,
    line_bot_api: AsyncMessagingApi, 
    user_id: str,
    message_text: str,
    reply_token: str,
    user_status,
    profile_data: Dict,
    session_id: str
):
    """จัดการข้อความในโหมด Live Chat"""
    
    # แจ้งผ้าน WebSocket ไป Admin UI
    await manager.broadcast({
        "type": "new_message",
        "userId": user_id,
        "message": message_text,
        "displayName": profile_data['display_name'],
        "pictureUrl": profile_data['picture_url'],
        "sessionId": session_id,
        "timestamp": datetime.now().isoformat()
    })
    
    # ถ้าเป็นโหมด auto ให้บอทตอบ
    if user_status.chat_mode == 'auto':
        await show_loading_animation(line_bot_api, user_id)
        
        bot_response = f"🤖 บอทตอบอัตโนมัติ: ได้รับข้อความ '{message_text}' แล้วครับ"
        
        # บันทึกการตอบของบอท
        await save_chat_history(
            db=db,
            user_id=user_id,
            message_type='bot',
            message_content=bot_response,
            session_id=session_id,
            extra_data={"auto_reply": True, "original_message": message_text}
        )
        
        await save_chat_message(db, user_id, 'bot', bot_response)
        
        try:
            reply_request = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=bot_response)]
            )
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db,
                level="error",
                category="line_webhook",
                subcategory="reply_failed",
                message=f"Failed to send auto reply: {str(e)}",
                user_id=user_id
            )
        
        # แจ้ง Admin UI ว่าบอทตอบแล้ว
        await manager.broadcast({
            "type": "bot_auto_reply",
            "userId": user_id,
            "message": bot_response,
            "sessionId": session_id
        })

async def handle_bot_mode_message(
    db: AsyncSession,
    line_bot_api: AsyncMessagingApi,
    user_id: str, 
    message_text: str,
    reply_token: str,
    profile_data: Dict,
    session_id: str
):
    """จัดการข้อความในโหมดบอท"""
    
    if "คุยกับแอดมิน" in message_text or "ติดต่อเจ้าหน้าที่" in message_text:
        # เปลี่ยนเป็นโหมด Live Chat
        await show_loading_animation(line_bot_api, user_id)
        
        await set_live_chat_status(
            db, user_id, True, profile_data['display_name'], profile_data['picture_url']
        )
        
        response_text = "รับทราบค่ะ กำลังโอนสายไปยังเจ้าหน้าที่ รอสักครู่นะคะ..."
        
        # บันทึกการตอบ
        await save_chat_history(
            db=db,
            user_id=user_id,
            message_type='bot',
            message_content=response_text,
            session_id=session_id,
            extra_data={"handoff_request": True, "trigger_message": message_text}
        )
        
        await save_chat_message(db, user_id, 'bot', response_text)
        
        try:
            reply_request = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=response_text)]
            )
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db,
                level="error", 
                category="line_webhook",
                subcategory="handoff_reply_failed",
                message=f"Failed to send handoff reply: {str(e)}",
                user_id=user_id
            )
        
        # ส่งแจ้งเตือนไป Telegram
        await send_telegram_notification_enhanced(
            db=db,
            notification_type="chat_request",
            title="🚨 แจ้งเตือนการขอแชท",
            message=f"จาก: {profile_data['display_name']}\nข้อความ: {message_text}",
            user_id=user_id,
            priority=3,
            data={
                "user_profile": profile_data,
                "trigger_message": message_text,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # แจ้ง Admin UI
        await manager.broadcast({
            "type": "new_user_request",
            "userId": user_id,
            "message": message_text,
            "displayName": profile_data['display_name'],
            "pictureUrl": profile_data['picture_url'],
            "sessionId": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    else:
        # บอทตอบปกติ
        await show_loading_animation(line_bot_api, user_id)
        
        response_text = "สวัสดีค่ะ! ขอบคุณที่ติดต่อเรามา หากต้องการคุยกับเจ้าหน้าที่ โปรดพิมพ์ 'ติดต่อเจ้าหน้าที่' ค่ะ"
        
        await save_chat_history(
            db=db,
            user_id=user_id,
            message_type='bot',
            message_content=response_text,
            session_id=session_id,
            extra_data={"standard_reply": True}
        )
        
        await save_chat_message(db, user_id, 'bot', response_text)
        
        try:
            reply_request = ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=response_text)]
            )
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db,
                level="error",
                category="line_webhook", 
                subcategory="bot_reply_failed",
                message=f"Failed to send bot reply: {str(e)}",
                user_id=user_id
            )

# ========================================
# Friend Event Handlers (NEW!)
# ========================================

async def handle_follow_event(event: FollowEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการเมื่อมีคนเพิ่มเป็นเพื่อน"""
    
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    # ดึงโปรไฟล์ผู้ใช้
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    
    # บันทึก Friend Activity
    await save_friend_activity(
        db=db,
        user_id=user_id,
        activity_type='follow',
        user_profile=profile_data,
        event_data={"event_type": "follow", "reply_token": reply_token},
        source='line_webhook'
    )
    
    # สร้าง/อัพเดท User Status
    await get_or_create_user_status(
        db, user_id, profile_data['display_name'], profile_data['picture_url']
    )
    
    # ส่งข้อความต้อนรับ
    welcome_message = f"สวัสดีค่ะ {profile_data['display_name']}! ยินดีต้อนรับสู่ระบบของเรา 🎉"
    
    try:
        reply_request = ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=welcome_message)]
        )
        await line_bot_api.reply_message(reply_request)
    except Exception as e:
        await log_system_event(
            db=db,
            level="error",
            category="line_webhook",
            subcategory="welcome_reply_failed", 
            message=f"Failed to send welcome message: {str(e)}",
            user_id=user_id
        )
    
    # ส่งแจ้งเตือนไป Telegram
    await send_telegram_notification_enhanced(
        db=db,
        notification_type="new_friend",
        title="👋 เพื่อนใหม่",
        message=f"ชื่อ: {profile_data['display_name']}\nUser ID: {user_id}",
        user_id=user_id,
        priority=1,
        data={
            "user_profile": profile_data,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"New friend: {profile_data['display_name']} ({user_id})")

async def handle_unfollow_event(event: UnfollowEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการเมื่อมีคนยกเลิกการติดตาม"""
    
    user_id = event.source.user_id
    
    # พยายามดึงข้อมูลผู้ใช้ (อาจจะไม่ได้เพราะ unfollow แล้ว)
    try:
        profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    except:
        profile_data = {"user_id": user_id, "display_name": f"User {user_id[-6:]}", "source": "fallback"}
    
    # บันทึก Friend Activity
    await save_friend_activity(
        db=db,
        user_id=user_id,
        activity_type='unfollow',
        user_profile=profile_data,
        event_data={"event_type": "unfollow"},
        source='line_webhook'
    )
    
    # อัพเดทสถานะผู้ใช้ (ออกจาก live chat ถ้ามี)
    await set_live_chat_status(db, user_id, False)
    
    # ส่งแจ้งเตือนไป Telegram
    await send_telegram_notification_enhanced(
        db=db,
        notification_type="friend_left",
        title="👋 เพื่อนออกจากระบบ", 
        message=f"ชื่อ: {profile_data['display_name']}\nUser ID: {user_id}",
        user_id=user_id,
        priority=1,
        data={
            "user_profile": profile_data,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"User unfollowed: {profile_data['display_name']} ({user_id})")

# ========================================
# Main Handler Function (Updated)
# ========================================

async def handle_message(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """Main message handler - ใช้ enhanced version"""
    await handle_message_enhanced(event, db, line_bot_api)

# Export new handlers
__all__ = [
    'handle_message_enhanced',
    'handle_follow_event', 
    'handle_unfollow_event',
    'send_telegram_notification_enhanced',
    'get_user_profile_enhanced'
]
