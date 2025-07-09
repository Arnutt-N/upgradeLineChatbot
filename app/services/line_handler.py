# app/services/line_handler.py
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest, PushMessageRequest, ShowLoadingAnimationRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app.core.config import settings
from app.db.crud import get_or_create_user_status, set_live_chat_status, save_chat_message
from app.services.ws_manager import manager

async def show_loading_animation(line_bot_api: AsyncMessagingApi, user_id: str):
    """แสดง loading animation ให้ผู้ใช้เห็น"""
    try:
        loading_request = ShowLoadingAnimationRequest(
            chat_id=user_id,
            loading_seconds=3  # แสดง animation 3 วินาที (ลดจาก 5 เป็น 3)
        )
        await line_bot_api.show_loading_animation(loading_request)
        print(f"✅ Loading animation sent to user: {user_id}")
    except Exception as e:
        print(f"❌ Error showing loading animation: {e}")
        # ไม่ให้ error นี้หยุดการทำงานของระบบ
        pass

async def get_user_profile(line_bot_api: AsyncMessagingApi, user_id: str):
    """ดึงโปรไฟล์ผู้ใช้จาก LINE API - ปรับปรุงให้ทำงานได้จริง"""
    try:
        # พยายามดึงข้อมูลจริงจาก LINE API
        print(f"🔍 Attempting to get profile for user: {user_id}")
        
        # ใช้ LINE Bot SDK v3 - ลองดึงข้อมูลจริง
        profile = await line_bot_api.get_profile(user_id)
        if profile and hasattr(profile, 'display_name'):
            print(f"✅ Successfully got profile: {profile.display_name}")
            return profile.display_name
        else:
            print(f"⚠️ Profile response exists but no display_name")
            
    except Exception as e:
        print(f"❌ Error getting user profile for {user_id}: {type(e).__name__}: {e}")
        
        # ลองใช้ httpx โดยตรงถ้า SDK ไม่ทำงาน
        try:
            print(f"🔄 Trying direct API call for user: {user_id}")
            return await get_user_profile_direct(user_id)
        except Exception as e2:
            print(f"❌ Direct API also failed: {type(e2).__name__}: {e2}")
    
    # ใช้ fallback name
    fallback_name = f"Customer {user_id[-6:]}"
    print(f"🔧 Using fallback name: {fallback_name}")
    return fallback_name

async def get_user_profile_direct(user_id: str):
    """ดึงโปรไฟล์ผู้ใช้โดยใช้ httpx โดยตรง"""
    try:
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
                display_name = data.get('displayName', f"Customer {user_id[-6:]}")
                print(f"✅ Direct API success: {display_name}")
                return display_name
            else:
                print(f"❌ Direct API failed with status: {response.status_code}")
                return f"Customer {user_id[-6:]}"
                
    except Exception as e:
        print(f"❌ Direct API exception: {type(e).__name__}: {e}")
        return f"Customer {user_id[-6:]}"

async def send_telegram_alert(message: str):
    """ส่งแจ้งเตือนผ่าน Telegram"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured")
        return
        
    api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {
        'chat_id': settings.TELEGRAM_CHAT_ID, 
        'text': message, 
        'parse_mode': 'Markdown'
    }
    
    try:
        timeout = httpx.Timeout(10.0)  # 10 seconds timeout
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            print(f"✅ Telegram alert sent successfully")
    except Exception as e:
        print(f"❌ Error sending Telegram alert: {e}")

async def handle_message(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการข้อความที่ได้รับจาก LINE"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_text = event.message.text

    print(f"📩 Message from {user_id}: {message_text}")
    
    # ดึงชื่อโปรไฟล์ผู้ใช้ก่อน (ทำก่อนเสมอ)
    user_display_name = await get_user_profile(line_bot_api, user_id)
    print(f"👤 User display name: {user_display_name}")

    # รับสถานะผู้ใช้ พร้อมอัปเดตชื่อ
    user_status = await get_or_create_user_status(db, user_id, user_display_name)

    if user_status.is_in_live_chat:
        # อยู่ในโหมด Live Chat: ตรวจสอบโหมดการทำงาน
        await save_chat_message(db, user_id, 'user', message_text)
        
        await manager.broadcast({
            "type": "new_message",
            "userId": user_id,
            "message": message_text,
            "displayName": user_display_name
        })
        
        # ถ้าเป็นโหมด auto ให้บอทตอบอัตโนมัติ
        if user_status.chat_mode == 'auto':
            # แสดง loading animation ก่อนตอบ
            await show_loading_animation(line_bot_api, user_id)
            
            bot_response = f"🤖 บอทตอบอัตโนมัติ: ได้รับข้อความ '{message_text}' แล้วครับ"
            await save_chat_message(db, user_id, 'bot', bot_response)
            
            try:
                reply_request = ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=bot_response)]
                )
                await line_bot_api.reply_message(reply_request)
            except Exception as e:
                print(f"Error sending LINE auto reply: {e}")
            
            # แจ้ง Admin UI ว่าบอทตอบแล้ว
            await manager.broadcast({
                "type": "bot_auto_reply",
                "userId": user_id,
                "message": bot_response
            })
        # ถ้าเป็นโหมด manual ไม่ต้องตอบอะไร รอแอดมินตอบ
    else:
        # อยู่ในโหมดบอท
        await save_chat_message(db, user_id, 'user', message_text)
        
        if "คุยกับแอดมิน" in message_text or "ติดต่อเจ้าหน้าที่" in message_text:
            # แสดง loading animation ขณะประมวลผล
            await show_loading_animation(line_bot_api, user_id)
            
            # เปลี่ยนเป็นโหมด Live Chat
            await set_live_chat_status(db, user_id, True, user_display_name)
            response_text = "รับทราบค่ะ กำลังโอนสายไปยังเจ้าหน้าที่ รอสักครู่นะคะ..."
            await save_chat_message(db, user_id, 'bot', response_text)
            
            try:
                # ส่ง reply message
                reply_request = ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=response_text)]
                )
                await line_bot_api.reply_message(reply_request)
            except Exception as e:
                print(f"Error sending LINE reply: {e}")
            
            # ส่งแจ้งเตือนไปยัง Telegram
            alert_message = f"🚨 *Human Handoff Request* 🚨\n\n*จาก:* {user_display_name}\n*ข้อความ:* {message_text}"
            await send_telegram_alert(alert_message)
            
            # แจ้งหน้า UI ว่ามี user ใหม่เข้ามา
            await manager.broadcast({
                "type": "new_user_request",
                "userId": user_id,
                "message": message_text,
                "displayName": user_display_name,  # ใช้ชื่อโปรไฟล์จริง
                "timestamp": datetime.now().isoformat()
            })
        else:
            # โหมดบอทปกติ - ตอบข้อความปกติ (ไม่เอคโค่)
            # แสดง loading animation ก่อนตอบ
            await show_loading_animation(line_bot_api, user_id)
            
            response_text = "สวัสดีค่ะ! ขอบคุณที่ติดต่อเรามา หากต้องการคุยกับเจ้าหน้าที่ โปรดพิมพ์ 'ติดต่อเจ้าหน้าที่' ค่ะ"
            await save_chat_message(db, user_id, 'bot', response_text)
            
            try:
                reply_request = ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=response_text)]
                )
                await line_bot_api.reply_message(reply_request)
            except Exception as e:
                print(f"Error sending LINE reply: {e}")
