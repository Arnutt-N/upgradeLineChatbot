# app/services/line_handler.py
import httpx
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncMessagingApi, TextMessage, ReplyMessageRequest, PushMessageRequest
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app.core.config import settings
from app.db.crud import get_or_create_user_status, set_live_chat_status, save_chat_message
from app.services.ws_manager import manager

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
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")

async def handle_message(event: MessageEvent, db: AsyncSession, line_bot_api: AsyncMessagingApi):
    """จัดการข้อความที่ได้รับจาก LINE"""
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_text = event.message.text

    # รับสถานะผู้ใช้
    user_status = await get_or_create_user_status(db, user_id)

    if user_status.is_in_live_chat:
        # อยู่ในโหมด Live Chat: ตรวจสอบโหมดการทำงาน
        await save_chat_message(db, user_id, 'user', message_text)
        await manager.broadcast({
            "type": "new_message",
            "userId": user_id,
            "message": message_text,
            "displayName": f"ลูกค้า {user_id[-6:]}"
        })
        
        # ถ้าเป็นโหมด auto ให้บอทตอบอัตโนมัติ
        if user_status.chat_mode == 'auto':
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
            # เปลี่ยนเป็นโหมด Live Chat
            await set_live_chat_status(db, user_id, True)
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
            alert_message = f"🚨 *Human Handoff Request* 🚨\n\n*จาก:* `{user_id}`\n*ข้อความ:* {message_text}"
            await send_telegram_alert(alert_message)
            
            # แจ้งหน้า UI ว่ามี user ใหม่เข้ามา
            await manager.broadcast({
                "type": "new_user_request",
                "userId": user_id,
                "message": message_text,
                "displayName": f"ลูกค้า {user_id[-6:]}",  # ใช้ 6 หลักสุดท้าย
                "timestamp": datetime.now().isoformat()
            })
        else:
            # โหมดบอทปกติ - ตอบข้อความปกติ (ไม่เอคโค่)
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
