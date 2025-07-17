# Enhanced LINE Handler with Comprehensive Tracking
import json
import uuid
import httpx
from datetime import datetime
from typing import Dict, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncMessagingApi, AsyncMessagingApiBlob, TextMessage, ReplyMessageRequest, PushMessageRequest
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

# Import AsyncMessagingApiBlob for handling multimedia content
from linebot.v3.messaging import AsyncMessagingApiBlob

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

async def show_loading_animation(line_bot_api: AsyncMessagingApi, user_id: str, seconds: int = 5):
    """Show loading animation in LINE app using direct API call matching curl format"""
    try:
        # LINE API requires loadingSeconds to be between 5-60 and multiple of 5
        loading_seconds = max(5, min(seconds, 60))  # Minimum 5, maximum 60
        # Round to nearest multiple of 5
        loading_seconds = round(loading_seconds / 5) * 5
        
        # Use direct HTTP API call with exact format from curl example
        import httpx
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}'
        }
        
        # Use exact payload format from curl example
        payload = {
            "chatId": user_id,
            "loadingSeconds": loading_seconds
        }
        
        # Validate user ID format (LINE user IDs start with 'U' and are 33 chars long)
        if not user_id.startswith('U') or len(user_id) != 33:
            print(f"Invalid user ID format: {user_id} (must be U + 32 hex chars)")
            return False
            
        print(f"Sending loading animation API call for user {user_id[-6:]}")
        print(f"URL: https://api.line.me/v2/bot/chat/loading/start")
        print(f"Payload: {payload}")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                'https://api.line.me/v2/bot/chat/loading/start',
                headers=headers,
                json=payload
            )
            
            print(f"Loading API response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"SUCCESS: Loading animation started for user {user_id[-6:]} ({loading_seconds}s)")
                return True
            elif response.status_code == 202:
                print(f"SUCCESS: Loading animation accepted for user {user_id[-6:]} ({loading_seconds}s)")
                return True
            elif response.status_code == 400:
                print(f"BAD REQUEST: Invalid parameters or user not in active chat")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 401:
                print(f"UNAUTHORIZED: Invalid access token")
                print(f"Response: {response.text}")
                return False
            elif response.status_code == 403:
                print(f"FORBIDDEN: User not in one-on-one chat or not viewing chat")
                print(f"Response: {response.text}")
                return False
            else:
                print(f"FAILED: Loading animation API returned {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"ERROR: Could not show loading animation: {e}")
        print(f"User ID: {user_id}, Seconds: {seconds}")
        return False

async def handle_image_message_enhanced(line_bot_api: AsyncMessagingApi, line_bot_blob_api: AsyncMessagingApiBlob, event: MessageEvent, db: AsyncSession):
    """
    Enhanced image message handler with Gemini AI analysis (based on jetpack reference)
    """
    user_id = event.source.user_id
    message_id = event.message.id
    
    try:
        # Show loading animation
        await show_loading_animation(line_bot_api, user_id, seconds=5)
        
        # Get user profile
        user_profile = await get_user_profile_enhanced(line_bot_api, user_id)
        
        # Get binary content of image from LINE server
        image_content = await line_bot_blob_api.get_message_content(message_id=message_id)
        
        # Save message to history first
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="user_image",
            message_content=f"[รูปภาพ] - Message ID: {message_id}",
            extra_data={"message_id": message_id, "content_type": "image"}
        )
        
        # Analyze image using Gemini AI
        gemini_response = await image_understanding(
            image_content=image_content,
            prompt="วิเคราะห์รูปภาพนี้เป็นภาษาไทย บอกรายละเอียดที่เห็นในภาพ และถ้าเป็นเอกสารหรือข้อความ ให้อ่านออกมาด้วยนะคะ"
        )
        
        print(f"Gemini image analysis: {gemini_response}")
        
        # Save AI response to history
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="ai_response",
            message_content=gemini_response,
            extra_data={"content_type": "image_analysis", "original_message_id": message_id}
        )
        
        # Reply with analysis result
        reply_message = TextMessage(text=gemini_response)
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )
        
        # Broadcast to admin interface
        await manager.broadcast({
            "type": "new_message",
            "userId": user_id,
            "message": f"[รูปภาพ] {gemini_response[:50]}...",
            "senderType": "user",
            "timestamp": get_thai_time().isoformat()
        })
        
        # Log system event
        await log_system_event(
            db=db,
            level="info",
            category="line_handler",
            subcategory="image_analysis",
            message=f"Image analyzed for user {user_id}",
            details={"response_length": len(gemini_response), "message_id": message_id}
        )
        
    except Exception as e:
        print(f"Error handling image message: {e}")
        
        # Save error to history
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="system_error",
            message_content=f"เกิดข้อผิดพลาดในการวิเคราะห์รูปภาพ: {str(e)[:100]}",
            extra_data={"error": str(e), "message_id": message_id}
        )
        
        # Send error message to user
        error_message = "ขออภัยค่ะ เกิดข้อผิดพลาดในการวิเคราะห์รูปภาพ กรุณาลองใหม่อีกครั้งหรือติดต่อเจ้าหน้าที่จ้า"
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=error_message)]
            )
        )

async def handle_file_message_enhanced(line_bot_api: AsyncMessagingApi, line_bot_blob_api: AsyncMessagingApiBlob, event: MessageEvent, db: AsyncSession):
    """
    Enhanced file message handler with Gemini AI document analysis (based on jetpack reference)
    """
    user_id = event.source.user_id
    message_id = event.message.id
    file_name = getattr(event.message, 'file_name', 'unknown_file')
    
    try:
        # Show loading animation for longer processing
        await show_loading_animation(line_bot_api, user_id, seconds=10)
        
        # Get user profile
        user_profile = await get_user_profile_enhanced(line_bot_api, user_id)
        
        # Check if it's a PDF file
        if not file_name.lower().endswith('.pdf'):
            error_message = "ขออภัยค่ะ ตอนนี้รองรับเฉพาะไฟล์ PDF เท่านั้นจ้า กรุณาส่งไฟล์ PDF มาใหม่นะคะ"
            await line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=error_message)]
                )
            )
            return
        
        # Get binary content of document from LINE server
        doc_content = await line_bot_blob_api.get_message_content(message_id=message_id)
        
        # Save message to history first
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="user_document",
            message_content=f"[เอกสาร PDF] {file_name}",
            extra_data={"message_id": message_id, "file_name": file_name, "content_type": "pdf"}
        )
        
        # Analyze document using Gemini AI
        gemini_response = await document_understanding(
            document_content=doc_content,
            prompt="สรุปเนื้อหาของเอกสาร PDF นี้เป็นภาษาไทย โดยเน้นประเด็นสำคัญและข้อมูลที่เป็นประโยชน์"
        )
        
        print(f"Gemini document analysis: {gemini_response}")
        
        # Save AI response to history
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="ai_response",
            message_content=gemini_response,
            extra_data={"content_type": "document_analysis", "original_message_id": message_id, "file_name": file_name}
        )
        
        # Reply with analysis result
        reply_message = TextMessage(text=f"📄 สรุปเอกสาร: {file_name}\n\n{gemini_response}")
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[reply_message]
            )
        )
        
        # Broadcast to admin interface
        await manager.broadcast({
            "type": "new_message",
            "userId": user_id,
            "message": f"[เอกสาร PDF] {file_name}: {gemini_response[:50]}...",
            "senderType": "user",
            "timestamp": get_thai_time().isoformat()
        })
        
        # Log system event
        await log_system_event(
            db=db,
            level="info",
            category="line_handler",
            subcategory="document_analysis",
            message=f"Document analyzed for user {user_id}: {file_name}",
            details={"response_length": len(gemini_response), "message_id": message_id, "file_name": file_name}
        )
        
    except Exception as e:
        print(f"Error handling file message: {e}")
        
        # Save error to history
        await save_chat_to_history(
            db=db,
            user_id=user_id,
            message_type="system_error",
            message_content=f"เกิดข้อผิดพลาดในการวิเคราะห์เอกสาร: {str(e)[:100]}",
            extra_data={"error": str(e), "message_id": message_id, "file_name": file_name}
        )
        
        # Send error message to user
        error_message = "ขออภัยค่ะ เกิดข้อผิดพลาดในการวิเคราะห์เอกสาร กรุณาลองใหม่อีกครั้งหรือติดต่อเจ้าหน้าที่จ้า"
        await line_bot_api.reply_message(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=error_message)]
            )
        )

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
    
    # บันทึกข้อความใน ChatHistory (ตารางใหม่)
    await save_chat_to_history(
        db=db, user_id=user_id, message_type='user', message_content=message_text,
        message_id=message_id, reply_token=reply_token, session_id=session_id,
        extra_data={"profile_data": profile_data, "timestamp": thai_time.isoformat()}
    )
    
    # บันทึกใน chat_messages เดิมด้วย (เพื่อ backward compatibility)
    await save_chat_message(db, user_id, 'user', message_text)
    
    user_status = await get_or_create_user_status(
        db, user_id, profile_data['display_name'], profile_data['picture_url']
    )
    
    # Broadcast new message to admin panel via WebSocket - only once
    await manager.broadcast({
        "type": "new_message",
        "userId": user_id,
        "message": message_text,
        "displayName": profile_data['display_name'],
        "pictureUrl": profile_data['picture_url'],
        "sessionId": session_id,
        "timestamp": thai_time.isoformat(),
        "senderType": "user"
    })
    
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
    
    # Handle auto mode with AI response
    if user_status.chat_mode == 'auto':
        await show_loading_animation(line_bot_api, user_id)
        
        # Broadcast typing indicator to admin
        await manager.broadcast({
            "type": "bot_typing_start",
            "userId": user_id,
            "timestamp": thai_time.isoformat()
        })
        
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
        
        await save_chat_to_history(
            db=db, user_id=user_id, message_type=message_type, message_content=bot_response,
            session_id=session_id, extra_data=extra_data
        )
        await save_chat_message(db, user_id, message_type, bot_response)
        
        try:
            # Ensure bot_response is clean and not empty
            if bot_response and bot_response.strip():
                reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=bot_response)])
                await line_bot_api.reply_message(reply_request)
                print(f"Reply sent successfully to user {user_id}")
            else:
                print(f"Empty bot response for user {user_id}")
                bot_response = "ขออภัย เกิดข้อผิดพลาดในการสร้างคำตอบ"
                reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=bot_response)])
                await line_bot_api.reply_message(reply_request)
        except Exception as e:
            print(f"Failed to send reply to user {user_id}: {e}")
            await log_system_event(
                db=db, level="error", category="line_webhook", subcategory="reply_failed",
                message=f"Failed to send auto reply: {str(e)}", user_id=user_id
            )
        
        # Stop typing indicator
        await manager.broadcast({
            "type": "bot_typing_stop",
            "userId": user_id,
            "timestamp": thai_time.isoformat()
        })
        
        # Broadcast bot response with unique identifier to prevent duplication
        await manager.broadcast({
            "type": "bot_auto_reply",
            "userId": user_id,
            "message": bot_response,
            "sessionId": session_id,
            "timestamp": thai_time.isoformat(),
            "messageId": f"bot_{user_id}_{int(thai_time.timestamp() * 1000)}"  # Unique ID
        })

async def handle_bot_mode_message(
    db: AsyncSession, line_bot_api: AsyncMessagingApi, user_id: str, 
    message_text: str, reply_token: str, profile_data: Dict, session_id: str
):
    """จัดการข้อความในโหมดบอทด้วย Gemini AI"""
    # Use Thai timezone
    thai_time = get_thai_time()
    
    # Check for live chat request keywords
    live_chat_keywords = ["คุยกับแอดมิน", "ติดต่อเจ้าหน้าที่", "admin", "help", "คุยกับคน"]
    
    if any(keyword in message_text.lower() for keyword in live_chat_keywords):
        await show_loading_animation(line_bot_api, user_id)
        await set_live_chat_status(db, user_id, True, profile_data['display_name'], profile_data['picture_url'])
        response_text = "รับทราบค่ะ! กำลังโอนสายไปยังเจ้าหน้าที่ให้นะคะ รอแป๊บนึงเดี๋ยวจะมีเจ้าหน้าที่มาคุยกับคุณค่ะ 💕"
        
        await save_chat_to_history(
            db=db, user_id=user_id, message_type='bot', message_content=response_text,
            session_id=session_id, extra_data={"handoff_request": True, "trigger_message": message_text}
        )
        await save_chat_message(db, user_id, 'bot', response_text)
        
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
            "type": "new_user_request", "userId": user_id, "message": message_text,
            "displayName": profile_data['display_name'], "pictureUrl": profile_data['picture_url'],
            "sessionId": session_id, "timestamp": thai_time.isoformat()
        })
    else:
        await show_loading_animation(line_bot_api, user_id)
        
        # Broadcast typing indicator to admin
        await manager.broadcast({
            "type": "bot_typing_start",
            "userId": user_id,
            "timestamp": thai_time.isoformat()
        })
        
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
        
        await save_chat_to_history(
            db=db, user_id=user_id, message_type=message_type, message_content=response_text,
            session_id=session_id, extra_data=extra_data
        )
        await save_chat_message(db, user_id, message_type, response_text)
        
        try:
            # Ensure response_text is clean and not empty
            if response_text and response_text.strip():
                reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
                await line_bot_api.reply_message(reply_request)
                print(f"Bot reply sent successfully to user {user_id}")
            else:
                print(f"Empty response_text for user {user_id}")
                response_text = "ขออภัย เกิดข้อผิดพลาดในการสร้างคำตอบ"
                reply_request = ReplyMessageRequest(reply_token=reply_token, messages=[TextMessage(text=response_text)])
                await line_bot_api.reply_message(reply_request)
        except Exception as e:
            print(f"Failed to send bot reply to user {user_id}: {e}")
            await log_system_event(
                db=db, level="error", category="line_webhook", subcategory="bot_reply_failed",
                message=f"Failed to send bot reply: {str(e)}", user_id=user_id
            )
        
        # Stop typing indicator after bot response is sent
        await manager.broadcast({
            "type": "bot_typing_stop",
            "userId": user_id,
            "timestamp": thai_time.isoformat()
        })
        
        # Broadcast bot response with unique identifier to prevent duplication
        await manager.broadcast({
            "type": "bot_auto_reply",
            "userId": user_id,
            "message": response_text,
            "sessionId": session_id,
            "timestamp": thai_time.isoformat(),
            "messageId": f"bot_{user_id}_{int(thai_time.timestamp() * 1000)}"  # Unique ID
        })

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

    # Broadcast friend status change via WebSocket
    await manager.broadcast({
        "type": "friend_status_change",
        "userId": user_id,
        "displayName": profile_data.get('display_name', f"Customer {user_id[-6:]}"),
        "pictureUrl": profile_data.get('picture_url'),
        "status": "followed",
        "timestamp": thai_time.isoformat()
    })

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

    # Broadcast friend status change via WebSocket
    await manager.broadcast({
        "type": "friend_status_change",
        "userId": user_id,
        "displayName": profile_data.get('display_name', f"User {user_id[-6:]}"),
        "pictureUrl": profile_data.get('picture_url', None), # Use None if not available
        "status": "unfollowed",
        "timestamp": thai_time.isoformat()
    })


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
