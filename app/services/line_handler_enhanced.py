# Enhanced LINE Handler with Comprehensive Tracking
import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncMessagingApi, AsyncMessagingApiBlob, TextMessage, ReplyMessageRequest, PushMessageRequest, ShowLoadingAnimationRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent, ImageMessageContent, FileMessageContent, FollowEvent, UnfollowEvent

from app.core.config import settings
# --- ส่วนนี้เป็นการ import จากไฟล์ crud.py เดิม สำหรับ backward compatibility ---
from app.db.crud import get_or_create_user_status, set_live_chat_status, save_chat_message

# --- ส่วนนี้เป็นการ import จากไฟล์ crud_enhanced.py ใหม่ ---
from app.db.crud_enhanced import (
    save_chat_to_history,  # <-- แก้ไขชื่อฟังก์ชันที่ import ให้ถูกต้อง
    save_friend_activity, 
    create_telegram_notification,
    log_system_event,
    update_notification_status # <-- เพิ่ม import นี้เข้ามา
)
from app.services.ws_manager import manager
from app.utils.timezone import get_thai_time

# --- Gemini AI Integration ---
from app.services.gemini_service import get_ai_response, check_gemini_availability, image_understanding, document_understanding

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
            return profile_data
            
    except Exception:
        # หาก SDK ล้มเหลว ให้ลองใช้ Direct API
        try:
            return await get_user_profile_direct_enhanced(user_id, profile_data)
        except Exception as e:
            print(f"Direct API failed: {e}")
            return profile_data # คืนค่า fallback สุดท้าย
    return profile_data # คืนค่า fallback หาก SDK ไม่ผ่านและไม่มีการเรียก direct

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
    
    notification = await create_telegram_notification(
        db=db, notification_type=notification_type, title=title, message=message,
        user_id=user_id, priority=priority, extra_data=data
    )
    
    await log_system_event(
        db=db, level="info", category="telegram", subcategory="notification_created",
        message=f"Created notification: {notification_type}",
        details={"notification_id": notification.id, "user_id": user_id}
    )
    
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        await log_system_event(
            db=db, level="warning", category="telegram", subcategory="config_missing",
            message="Telegram credentials not configured",
            details={"notification_id": notification.id}
        )
        return False
    
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
    
    formatted_message = f"*{title}*\n\n{message}"
    if data and 'timestamp' in data:
        formatted_message += f"\n\n_เวลา: {data['timestamp']}_"
    
    params = {'chat_id': settings.TELEGRAM_CHAT_ID, 'text': formatted_message, 'parse_mode': 'Markdown'}
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            
            await update_notification_status(
                db=db, notification_id=notification_id, status='sent',
                telegram_message_id=response.json().get('result', {}).get('message_id')
            )
            await log_system_event(
                db=db, level="info", category="telegram", subcategory="message_sent",
                message="Telegram message sent successfully", details={"notification_id": notification_id}
            )
            return True
            
    except Exception as e:
        await update_notification_status(
            db=db, notification_id=notification_id, status='failed', error_message=str(e)
        )
        await log_system_event(
            db=db, level="error", category="telegram", subcategory="send_failed", 
            message=f"Failed to send Telegram message: {str(e)}",
            details={"notification_id": notification_id, "error": str(e)}
        )
        return False

# ========================================
# Enhanced Event Handlers
# ========================================

async def show_loading_animation(line_bot_api: AsyncMessagingApi, user_id: str, seconds: int = 3):
    """แสดง loading animation พร้อมการกำหนดเวลาและ fallback graceful"""
    try:
        # Maximum allowed loading time is 60 seconds
        loading_seconds = min(seconds, 60)
        
        loading_request = ShowLoadingAnimationRequest(
            chat_id=user_id,
            loading_seconds=loading_seconds
        )
        await line_bot_api.show_loading_animation(loading_request)
        print(f"✅ Loading animation shown for user {user_id} ({loading_seconds}s)")
        
        # Also broadcast to admin panel for visual feedback
        from app.services.ws_manager import manager
        await manager.broadcast({
            "type": "user_typing",
            "userId": user_id,
            "isTyping": True,
            "loadingSeconds": loading_seconds,
            "timestamp": get_thai_time().isoformat()
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"⚠️  Loading animation failed for user {user_id}: {error_msg}")
        
        # Provide fallback visual feedback in admin panel
        try:
            from app.services.ws_manager import manager
            await manager.broadcast({
                "type": "user_typing",
                "userId": user_id,
                "isTyping": True,
                "fallback": True,
                "loadingSeconds": seconds,
                "error": "LINE loading animation unavailable",
                "timestamp": get_thai_time().isoformat()
            })
        except Exception as broadcast_e:
            print(f"❌ Failed to broadcast loading fallback: {broadcast_e}")
        
        # Don't raise the exception - this shouldn't break the chat flow
        return False
    
    return True

async def handle_message_enhanced(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการข้อความ - Enhanced version with comprehensive tracking"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_text = event.message.text
    message_id = getattr(event.message, 'id', None)
    # Use Thai timezone for session ID
    thai_time = get_thai_time()
    session_id = f"session_{user_id}_{thai_time.strftime('%Y%m%d')}"
    
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    
    # บันทึกข้อความใน ChatHistory only (remove dual storage)
    try:
        await save_chat_to_history(
            db=db, user_id=user_id, message_type='user', message_content=message_text,
            message_id=message_id, reply_token=reply_token, session_id=session_id,
            extra_data={"profile_data": profile_data, "timestamp": thai_time.isoformat()}
        )
        print(f"SUCCESS: User message saved to chat_history: {user_id}")
    except Exception as e:
        print(f"ERROR: Failed to save user message to chat_history: {e}")
        # Fallback: try saving to old table
        try:
            await save_chat_message(db, user_id, 'user', message_text)
            print(f"SUCCESS: User message saved to chat_messages (fallback): {user_id}")
        except Exception as e2:
            print(f"ERROR: Failed to save user message to any table: {e2}")
    
    user_status = await get_or_create_user_status(
        db, user_id, profile_data['display_name'], profile_data['picture_url']
    )
    
    # Broadcast new message to admin panel via WebSocket with consistent format
    broadcast_data = {
        "type": "new_message",
        "userId": user_id,
        "message": message_text,
        "messageId": f"user_{user_id}_{message_id}_{int(thai_time.timestamp() * 1000)}" if message_id else f"user_{user_id}_{int(thai_time.timestamp() * 1000)}",
        "displayName": profile_data['display_name'],
        "pictureUrl": profile_data['picture_url'],
        "sessionId": session_id,
        "timestamp": thai_time.isoformat(),
        "senderType": "user",
        "isRead": False,
        "chatMode": getattr(user_status, 'chat_mode', 'manual'),
        "isInLiveChat": getattr(user_status, 'is_in_live_chat', False)
    }
    
    print(f"Broadcasting new message from user {user_id}: {message_text[:50]}...")
    await manager.broadcast(broadcast_data)
    
    if user_status.is_in_live_chat:
        await handle_live_chat_message(
            db, line_bot_api, user_id, message_text, reply_token, 
            user_status, profile_data, session_id
        )
    else:
        await handle_bot_mode_message(
            db, line_bot_api, user_id, message_text, reply_token,
            profile_data, session_id
        )

async def handle_live_chat_message(
    db: AsyncSession, line_bot_api: AsyncMessagingApi, user_id: str,
    message_text: str, reply_token: str, user_status,
    profile_data: Dict, session_id: str
):
    """จัดการข้อความในโหมด Live Chat"""
    # Use Thai timezone
    thai_time = get_thai_time()
    
    await manager.broadcast({
        "type": "live_chat_message", 
        "userId": user_id, 
        "message": message_text,
        "displayName": profile_data['display_name'], 
        "pictureUrl": profile_data['picture_url'],
        "sessionId": session_id, 
        "timestamp": thai_time.isoformat(),
        "senderType": "user",
        "chatMode": user_status.chat_mode
    })
    
    # Handle auto mode with AI response
    if user_status.chat_mode == 'auto':
        await show_loading_animation(line_bot_api, user_id)
        
        # Try to get AI response using Gemini
        ai_available = await check_gemini_availability()
        if ai_available:
            try:
                # Import GeminiService for proper system prompt handling
                from app.services.gemini_service import gemini_service
                
                # Generate smart reply with system prompt
                result = await gemini_service.generate_smart_reply(
                    user_message=message_text,
                    user_profile=profile_data,
                    db=db
                )
                
                if result["success"]:
                    bot_response = result["response"]
                    message_type = 'ai_bot'
                    extra_data = {
                        "auto_reply": True,
                        "ai_powered": True,
                        "gemini_response": True,
                        "model": result.get("model"),
                        "usage": result.get("usage"),
                        "original_message": message_text
                    }
                else:
                    # Fallback response for AI failure
                    bot_response = f"ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือรอให้เจ้าหน้าที่ตอบกลับค่ะ"
                    message_type = 'bot'
                    extra_data = {
                        "auto_reply": True,
                        "ai_fallback": True,
                        "ai_error": result.get("error"),
                        "original_message": message_text
                    }
                    
            except Exception as e:
                # Exception fallback
                await log_system_event(
                    db=db, level="warning", category="gemini", subcategory="live_chat_ai_fallback",
                    message=f"AI response failed in live chat: {str(e)}", user_id=user_id
                )
                bot_response = f"ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือรอให้เจ้าหน้าที่ตอบกลับค่ะ"
                message_type = 'bot'
                extra_data = {
                    "auto_reply": True,
                    "ai_fallback": True,
                    "exception": str(e),
                    "original_message": message_text
                }
        else:
            # Basic auto reply when AI is not available
            bot_response = f"ขออภัย ระบบ AI ไม่พร้อมใช้งาน กรุณารอให้เจ้าหน้าที่ตอบกลับค่ะ"
            message_type = 'bot'
            extra_data = {
                "auto_reply": True,
                "ai_unavailable": True,
                "original_message": message_text
            }
        
        try:
            await save_chat_to_history(
                db=db, user_id=user_id, message_type=message_type, message_content=bot_response,
                session_id=session_id, extra_data=extra_data
            )
            print(f"SUCCESS: Bot response saved to chat_history: {user_id}")
        except Exception as e:
            print(f"ERROR: Failed to save bot response to chat_history: {e}")
            # Fallback: try saving to old table
            try:
                await save_chat_message(db, user_id, message_type, bot_response)
                print(f"SUCCESS: Bot response saved to chat_messages (fallback): {user_id}")
            except Exception as e2:
                print(f"ERROR: Failed to save bot response to any table: {e2}")
        
        try:
            reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=bot_response)])
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="line_webhook", subcategory="reply_failed",
                message=f"Failed to send auto reply: {str(e)}", user_id=user_id
            )
        
        await manager.broadcast({
            "type": "bot_auto_reply", 
            "userId": user_id, 
            "message": bot_response, 
            "sessionId": session_id,
            "timestamp": thai_time.isoformat(),
            "senderType": "bot",
            "messageType": message_type,
            "displayName": "AI Assistant"
        })

async def handle_bot_mode_message(
    db: AsyncSession, line_bot_api: AsyncMessagingApi, user_id: str, 
    message_text: str, reply_token: str, profile_data: Dict, session_id: str
):
    """จัดการข้อความในโหมดบอทด้วย Gemini AI"""
    # Use Thai timezone
    thai_time = get_thai_time()
    
    # Check for live chat request keywords
    live_chat_keywords = ["คุยกับแอดมิน", "ติดต่อเจ้าหน้าที่", "admin", "help", "คุยกับคน", "0"]
    
    if any(keyword in message_text.lower() for keyword in live_chat_keywords):
        await show_loading_animation(line_bot_api, user_id)
        await set_live_chat_status(db, user_id, True, profile_data['display_name'], profile_data['picture_url'])
        response_text = "รับทราบค่ะ! กำลังโอนสายไปยังเจ้าหน้าที่ให้นะคะ รอแป๊บนึงเดี๋ยวจะมีเจ้าหน้าที่มาคุยกับคุณค่ะ 💕"
        
        try:
            await save_chat_to_history(
                db=db, user_id=user_id, message_type='bot', message_content=response_text,
                session_id=session_id, extra_data={"handoff_request": True, "trigger_message": message_text}
            )
            print(f"SUCCESS: Handoff message saved to chat_history: {user_id}")
        except Exception as e:
            print(f"ERROR: Failed to save handoff message to chat_history: {e}")
            try:
                await save_chat_message(db, user_id, 'bot', response_text)
                print(f"SUCCESS: Handoff message saved to chat_messages (fallback): {user_id}")
            except Exception as e2:
                print(f"ERROR: Failed to save handoff message to any table: {e2}")
        
        try:
            reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="line_webhook", subcategory="handoff_reply_failed",
                message=f"Failed to send handoff reply: {str(e)}", user_id=user_id
            )
        
        await send_telegram_notification_enhanced(
            db=db, notification_type="chat_request", title="🚨 แจ้งเตือนการขอแชท",
            message=f"จาก: {profile_data['display_name']}\nข้อความ: {message_text}",
            user_id=user_id, priority=3,
            data={"user_profile": profile_data, "trigger_message": message_text, "timestamp": thai_time.isoformat()}
        )
        
        await manager.broadcast({
            "type": "new_user_request", 
            "userId": user_id, 
            "message": message_text,
            "displayName": profile_data['display_name'], 
            "pictureUrl": profile_data['picture_url'],
            "sessionId": session_id, 
            "timestamp": thai_time.isoformat(),
            "senderType": "user",
            "requestType": "chat_handoff",
            "priority": "high"
        })
    else:
        await show_loading_animation(line_bot_api, user_id)
        
        # Try to get AI response using Gemini with proper system prompt
        ai_available = await check_gemini_availability()
        if ai_available:
            try:
                # Import GeminiService for proper system prompt handling
                from app.services.gemini_service import gemini_service
                
                # Generate smart reply with system prompt
                result = await gemini_service.generate_smart_reply(
                    user_message=message_text,
                    user_profile=profile_data,
                    db=db
                )
                
                if result["success"]:
                    response_text = result["response"]
                    message_type = 'ai_bot'
                    extra_data = {
                        "ai_powered": True, 
                        "gemini_response": True,
                        "model": result.get("model"),
                        "usage": result.get("usage")
                    }
                else:
                    # Log AI failure and use fallback
                    await log_system_event(
                        db=db, level="warning", category="gemini", subcategory="ai_generation_failed",
                        message=f"AI generation failed: {result.get('error', 'Unknown error')}", user_id=user_id
                    )
                    response_text = "ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือพิมพ์ 'ติดต่อเจ้าหน้าที่' เพื่อคุยกับคน"
                    message_type = 'bot'
                    extra_data = {"standard_reply": True, "ai_fallback": True, "ai_error": result.get("error")}
                    
            except Exception as e:
                # Fallback to standard response if AI fails
                await log_system_event(
                    db=db, level="warning", category="gemini", subcategory="ai_fallback",
                    message=f"AI response failed, using fallback: {str(e)}", user_id=user_id
                )
                response_text = "ขออภัย เกิดข้อผิดพลาดในระบบ AI กรุณาลองใหม่อีกครั้ง หรือพิมพ์ 'ติดต่อเจ้าหน้าที่' เพื่อคุยกับคน"
                message_type = 'bot'
                extra_data = {"standard_reply": True, "ai_fallback": True, "exception": str(e)}
        else:
            # Standard response when AI is not available
            response_text = "สวัสดีค่ะ! ดีใจที่ได้พบกับคุณนะคะ 😊 หากต้องการคุยกับเจ้าหน้าที่ โปรดพิมพ์ 'ติดต่อเจ้าหน้าที่' ได้เลยค่ะ"
            message_type = 'bot'
            extra_data = {"standard_reply": True, "ai_unavailable": True}
        
        try:
            await save_chat_to_history(
                db=db, user_id=user_id, message_type=message_type, message_content=response_text,
                session_id=session_id, extra_data=extra_data
            )
            print(f"SUCCESS: Standard response saved to chat_history: {user_id}")
        except Exception as e:
            print(f"ERROR: Failed to save standard response to chat_history: {e}")
            try:
                await save_chat_message(db, user_id, message_type, response_text)
                print(f"SUCCESS: Standard response saved to chat_messages (fallback): {user_id}")
            except Exception as e2:
                print(f"ERROR: Failed to save standard response to any table: {e2}")
        
        try:
            reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
            await line_bot_api.reply_message(reply_request)
        except Exception as e:
            await log_system_event(
                db=db, level="error", category="line_webhook", subcategory="bot_reply_failed",
                message=f"Failed to send bot reply: {str(e)}", user_id=user_id
            )

# ========================================
# Friend Event Handlers
# ========================================

async def handle_follow_event(event: FollowEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการเมื่อมีคนเพิ่มเป็นเพื่อน"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    
    # Use Thai timezone
    thai_time = get_thai_time()
    
    await save_friend_activity(
        db=db, user_id=user_id, activity_type='follow', user_profile=profile_data,
        event_data={"event_type": "follow", "reply_token": reply_token}, source='line_webhook'
    )
    await get_or_create_user_status(db, user_id, profile_data['display_name'], profile_data['picture_url'])
    
    welcome_message = f"สวัสดีค่ะ คุณ{profile_data['display_name']}! ยินดีต้อนรับสู่ระบบของเราค่ะ 🎉✨ ดีใจที่ได้รู้จักนะคะ มีอะไรให้ช่วยเหลือไหมคะ?"
    try:
        reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=welcome_message)])
        await line_bot_api.reply_message(reply_request)
    except Exception as e:
        await log_system_event(
            db=db, level="error", category="line_webhook", subcategory="welcome_reply_failed", 
            message=f"Failed to send welcome message: {str(e)}", user_id=user_id
        )
    
    await send_telegram_notification_enhanced(
        db=db, notification_type="new_friend", title="🎉 เพื่อนใหม่เข้าร่วม",
        message=f"""👤 ชื่อ: {profile_data['display_name']}
🆔 User ID: {user_id}
🕐 เวลา: {thai_time.strftime('%Y-%m-%d %H:%M:%S')}
📱 ภาษา: {profile_data.get('language', 'ไม่ทราบ')}
💬 สถานะ: {profile_data.get('status_message', 'ไม่มีสถานะ')}
📸 รูปโปรไฟล์: {'✅ มี' if profile_data.get('picture_url') else '❌ ไม่มี'}

🎊 ยินดีต้อนรับสู่ระบบ!""",
        user_id=user_id, priority=1,
        data={"user_profile": profile_data, "timestamp": thai_time.isoformat(), "event_type": "new_friend"}
    )

async def handle_unfollow_event(event: UnfollowEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการเมื่อมีคนยกเลิกการติดตาม"""
    user_id = event.source.user_id
    profile_data = {"user_id": user_id, "display_name": f"User {user_id[-6:]}", "source": "fallback"}
    
    # Use Thai timezone
    thai_time = get_thai_time()
    
    await save_friend_activity(
        db=db, user_id=user_id, activity_type='unfollow', user_profile=profile_data,
        event_data={"event_type": "unfollow"}, source='line_webhook'
    )
    await set_live_chat_status(db, user_id, False)
    
    # Try to get the last known profile data
    try:
        from sqlalchemy import select, desc
        result = await db.execute(
            select(UserStatus.display_name, UserStatus.picture_url)
            .where(UserStatus.user_id == user_id)
        )
        user_status = result.first()
        if user_status:
            profile_data["display_name"] = user_status.display_name or f"User {user_id[-6:]}"
            profile_data["had_picture"] = "✅ มี" if user_status.picture_url else "❌ ไม่มี"
    except:
        pass
    
    await send_telegram_notification_enhanced(
        db=db, notification_type="friend_left", title="😔 เพื่อนออกจากระบบ", 
        message=f"""👤 ชื่อ: {profile_data['display_name']}
🆔 User ID: {user_id}
🕐 เวลา: {thai_time.strftime('%Y-%m-%d %H:%M:%S')}
📸 รูปโปรไฟล์: {profile_data.get('had_picture', 'ไม่ทราบ')}

💔 ขอบคุณที่เคยใช้บริการของเรา""",
        user_id=user_id, priority=1,
        data={"user_profile": profile_data, "timestamp": thai_time.isoformat(), "event_type": "friend_left"}
    )

# ========================================
# Image and File Message Handlers
# ========================================

async def handle_image_message_enhanced(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการข้อความที่เป็นรูปภาพ"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_id = event.message.id
    
    # Show loading animation
    try:
        # Loading animation disabled for compatibility
        pass
    except Exception:
        pass  # Loading animation might not be available in all plans
    
    # Get user profile
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    await get_or_create_user_status(db, user_id, profile_data['display_name'], profile_data['picture_url'])
    
    # Log image message
    await save_chat_to_history(
        db=db, user_id=user_id, message_type='user_image', 
        message_content=f"ส่งรูปภาพ (Message ID: {message_id})",
        session_id=f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        extra_data={"message_id": message_id, "content_type": "image"}
    )
    await save_chat_message(db, user_id, 'user', f"[รูปภาพ] ID: {message_id}")
    
    try:
        # Create blob API client for downloading content
        from linebot.v3.messaging import AsyncApiClient, Configuration
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        line_bot_blob_api = AsyncMessagingApiBlob(async_api_client)
        
        # Download image content
        message_content = await line_bot_blob_api.get_message_content(message_id=message_id)
        
        # Analyze image with Gemini
        gemini_response = await image_understanding(message_content)
        
        # Reply with analysis
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=gemini_response)]
            )
        )
        
        # Log AI response
        await save_chat_to_history(
            db=db, user_id=user_id, message_type='ai_image_analysis', 
            message_content=gemini_response,
            session_id=f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            extra_data={"message_id": message_id, "ai_powered": True}
        )
        await save_chat_message(db, user_id, 'ai_bot', gemini_response)
        
        # Notify admin about image
        await send_telegram_notification_enhanced(
            db=db, notification_type="image_received", title="📸 รูปภาพใหม่",
            message=f"ผู้ใช้: {profile_data['display_name']}\nการวิเคราะห์: {gemini_response[:100]}...",
            user_id=user_id, priority=2,
            data={"message_id": message_id, "analysis": gemini_response}
        )
        
    except Exception as e:
        error_message = "ขออภัย ไม่สามารถวิเคราะห์รูปภาพได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"
        
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=error_message)]
            )
        )
        
        await log_system_event(
            db=db, level="error", category="gemini", subcategory="image_analysis_failed",
            message=f"Failed to analyze image: {str(e)}", user_id=user_id
        )

async def handle_file_message_enhanced(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการข้อความที่เป็นไฟล์เอกสาร"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_id = event.message.id
    file_name = getattr(event.message, 'file_name', 'unknown_file')
    file_size = getattr(event.message, 'file_size', 0)
    
    # Show loading animation
    try:
        # Loading animation disabled for compatibility
        pass
    except Exception:
        pass
    
    # Get user profile
    profile_data = await get_user_profile_enhanced(line_bot_api, user_id)
    await get_or_create_user_status(db, user_id, profile_data['display_name'], profile_data['picture_url'])
    
    # Log file message
    await save_chat_to_history(
        db=db, user_id=user_id, message_type='user_file', 
        message_content=f"ส่งไฟล์: {file_name} ({file_size} bytes)",
        session_id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        extra_data={"message_id": message_id, "file_name": file_name, "file_size": file_size}
    )
    await save_chat_message(db, user_id, 'user', f"[ไฟล์] {file_name}")
    
    try:
        # Check file size limit (10MB)
        if file_size > 10 * 1024 * 1024:
            error_message = "ขออภัย ไฟล์มีขนาดใหญ่เกินไป (เกิน 10MB) กรุณาส่งไฟล์ที่มีขนาดเล็กกว่า"
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_message)])
            )
            return
        
        # Check if it's a PDF file
        if not file_name.lower().endswith('.pdf'):
            error_message = "ขออภัย ระบบรองรับเฉพาะไฟล์ PDF เท่านั้น กรุณาส่งไฟล์ในรูปแบบ PDF"
            await line_bot_api.reply_message(
                ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=error_message)])
            )
            return
        
        # Create blob API client for downloading content
        from linebot.v3.messaging import AsyncApiClient, Configuration
        configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
        async_api_client = AsyncApiClient(configuration)
        line_bot_blob_api = AsyncMessagingApiBlob(async_api_client)
        
        # Download file content
        file_content = await line_bot_blob_api.get_message_content(message_id=message_id)
        
        # Analyze document with Gemini
        gemini_response = await document_understanding(file_content)
        
        # Reply with analysis
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=gemini_response)]
            )
        )
        
        # Log AI response
        await save_chat_to_history(
            db=db, user_id=user_id, message_type='ai_document_analysis', 
            message_content=gemini_response,
            session_id=f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            extra_data={"message_id": message_id, "file_name": file_name, "ai_powered": True}
        )
        await save_chat_message(db, user_id, 'ai_bot', gemini_response)
        
        # Notify admin about document
        await send_telegram_notification_enhanced(
            db=db, notification_type="document_received", title="📄 เอกสารใหม่",
            message=f"ผู้ใช้: {profile_data['display_name']}\nไฟล์: {file_name}\nการวิเคราะห์: {gemini_response[:100]}...",
            user_id=user_id, priority=2,
            data={"message_id": message_id, "file_name": file_name, "analysis": gemini_response}
        )
        
    except Exception as e:
        error_message = "ขออภัย ไม่สามารถวิเคราะห์เอกสารได้ในขณะนี้ กรุณาลองใหม่อีกครั้ง"
        
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=error_message)]
            )
        )
        
        await log_system_event(
            db=db, level="error", category="gemini", subcategory="document_analysis_failed",
            message=f"Failed to analyze document: {str(e)}", user_id=user_id
        )

# Export handlers
__all__ = [
    'handle_message_enhanced',
    'handle_image_message_enhanced',
    'handle_file_message_enhanced',
    'handle_follow_event', 
    'handle_unfollow_event',
    'send_telegram_notification_enhanced',
    'get_user_profile_enhanced'
]
