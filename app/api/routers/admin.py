# app/api/routers/admin.py (ฉบับแก้ไข)
from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import pytz
from linebot.v3.messaging import (
    AsyncApiClient, AsyncMessagingApi, Configuration, 
    TextMessage, PushMessageRequest
    # ShowLoadingAnimationRequest removed for compatibility  
)

from app.core.config import settings
from app.db.database import get_db
from app.db.crud import (
    # ฟังก์ชันที่ยังใช้งานได้เพราะเกี่ยวกับ UserStatus
    set_live_chat_status, 
    set_chat_mode,
    get_or_create_user_status
)
# =======================================================================
# หมายเหตุ: แก้ไขการ import ให้ไปดึงฟังก์ชันที่ทำงานกับ 'ChatHistory'
# ชื่อฟังก์ชันเหล่านี้เป็นตัวอย่าง คุณต้องใช้ชื่อฟังก์ชันจริงๆ ที่คุณสร้างไว้
from app.db.crud_enhanced import (
    save_chat_to_history,
    get_all_chat_history_by_user,
    get_users_with_history,
    get_latest_chat_in_history
)
# =======================================================================
from app.schemas.chat import ReplyPayload, EndChatPayload, ToggleModePayload
from app.services.ws_manager import manager

# ตั้งค่า Templates - อ้างอิงจาก root project directory
templates = Jinja2Templates(directory="templates")

def get_line_bot_api():
    """สร้าง LINE Bot API client"""
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    return AsyncMessagingApi(async_api_client)

router = APIRouter()

@router.get("/", response_class=HTMLResponse, summary="หน้าแรก")
async def get_home_page(request: Request):
    """Redirect to admin page"""
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse, summary="แสดงหน้า Live Chat สำหรับแอดมิน")
async def get_admin_page(request: Request):
    """Endpoint สำหรับแสดงไฟล์ admin.html"""
    return templates.TemplateResponse("admin.html", {"request": request})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint สำหรับ WebSocket ที่หน้า Admin UI จะเชื่อมต่อเข้ามา"""
    await manager.connect(websocket)
    try:
        while True:
            # รอรับข้อมูล (แต่ในเคสนี้เราใช้สำหรับส่งออกอย่างเดียว)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/admin/reply", summary="API สำหรับแอดมินส่งข้อความตอบกลับ")
async def admin_reply(payload: ReplyPayload, db: AsyncSession = Depends(get_db)):
    try:
        line_bot_api = get_line_bot_api()
        
        # 1. แสดง loading animation (disabled for compatibility)
        try:
            # ShowLoadingAnimationRequest not available in current SDK version
            pass
        except Exception as e:
            print(f"Error showing loading animation: {e}")
        
        # 2. บันทึกข้อความของแอดมินลง DB (ใช้ฟังก์ชันใหม่)
        await save_chat_to_history(
            db=db, 
            user_id=payload.user_id, 
            message_type='admin', 
            message_content=payload.message
        )
        
        # 3. ส่ง Push Message ไปยังผู้ใช้ผ่าน LINE API
        try:
            push_request = PushMessageRequest(
                to=payload.user_id,
                messages=[TextMessage(text=payload.message)]
            )
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE push message: {e}")

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/end_chat", summary="API สำหรับจบการสนทนา")
async def end_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    try:
        line_bot_api = get_line_bot_api()
        await set_live_chat_status(db, payload.user_id, False)
        
        end_message = "เจ้าหน้าที่ได้จบการสนทนาแล้วค่ะ หากมีคำถามเพิ่มเติม สามารถพิมพ์เพื่อคุยกับบอทได้เลยค่ะ"
        
        try:
            push_request = PushMessageRequest(to=payload.user_id, messages=[TextMessage(text=end_message)])
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE end chat message: {e}")
            
        # บันทึกข้อความของบอท (ใช้ฟังก์ชันใหม่)
        await save_chat_to_history(db=db, user_id=payload.user_id, message_type='bot', message_content=end_message)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/toggle_mode", summary="API สำหรับสลับโหมดการแชท")
async def toggle_mode(payload: ToggleModePayload, db: AsyncSession = Depends(get_db)):
    try:
        await set_chat_mode(db, payload.user_id, payload.mode)
        
        mode_text = "แอดมินจะตอบเอง" if payload.mode == 'manual' else "บอทจะตอบอัตโนมัติ"
        notification = f"🔄 โหมดการตอบเปลี่ยนเป็น: {mode_text}"
        
        await manager.broadcast({
            "type": "mode_changed", "userId": payload.user_id,
            "mode": payload.mode, "message": notification
        })
        
        return {"status": "ok", "mode": payload.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/restart_chat", summary="API สำหรับเริ่มการสนทนาใหม่")
async def restart_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    try:
        line_bot_api = get_line_bot_api()
        await set_live_chat_status(db, payload.user_id, True)

        restart_message = "🟢 เจ้าหน้าที่พร้อมให้บริการแล้วค่ะ สามารถสอบถามได้เลยค่ะ"
        
        try:
            push_request = PushMessageRequest(to=payload.user_id, messages=[TextMessage(text=restart_message)])
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE restart message: {e}")
            
        # บันทึกข้อความของบอท (ใช้ฟังก์ชันใหม่)
        await save_chat_to_history(db=db, user_id=payload.user_id, message_type='bot', message_content=restart_message)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/users", summary="API สำหรับโหลดรายการผู้ใช้ทั้งหมด")
async def get_users_list(db: AsyncSession = Depends(get_db)):
    try:
        # ใช้ฟังก์ชันใหม่ในการดึงรายชื่อผู้ใช้
        users_data = await get_users_with_history(db)
        users_list = []
        
        for user_data in users_data:
            user_id = user_data.user_id
            
            # ใช้ฟังก์ชันใหม่ในการดึงข้อความล่าสุด
            latest_message = await get_latest_chat_in_history(db, user_id)
            
            users_list.append({
                "user_id": user_id,
                "display_name": user_data.display_name or f"Customer {user_id[-6:]}",
                "picture_url": user_data.picture_url,
                "is_in_live_chat": user_data.is_in_live_chat,
                "chat_mode": user_data.chat_mode,
                # แก้ไขชื่อคอลัมน์ให้ตรงกับ ChatHistory
                "latest_message": latest_message.message_content if latest_message else "ยังไม่มีการแชท",
                "last_activity": latest_message.timestamp.isoformat() if latest_message else None
            })
        
        return {"users": users_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/messages/{user_id}", summary="API สำหรับโหลดข้อความของผู้ใช้")
async def get_user_messages(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        # ใช้ฟังก์ชันใหม่ในการดึงประวัติแชท
        messages = await get_all_chat_history_by_user(db, user_id)
        messages_list = []
        
        # Thai timezone
        thai_tz = pytz.timezone('Asia/Bangkok')
        
        for msg in messages:
            # Convert timestamp to Thai timezone
            if msg.timestamp.tzinfo is None:
                # If naive datetime, assume it's UTC
                utc_time = pytz.utc.localize(msg.timestamp)
            else:
                utc_time = msg.timestamp.astimezone(pytz.utc)
            
            thai_time = utc_time.astimezone(thai_tz)
            
            messages_list.append({
                "id": msg.id,
                # แก้ไขชื่อคอลัมน์ให้ตรงกับ ChatHistory
                "message": msg.message_content,
                "sender_type": msg.message_type,
                "created_at": thai_time.isoformat()
            })
        
        return {"messages": messages_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/status", summary="API สำหรับตรวจสอบสถานะระบบ")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """ตรวจสอบสถานะระบบและการเชื่อมต่อ"""
    try:
        from app.services.gemini_service import check_gemini_availability
        
        # Check Gemini AI availability
        ai_available = await check_gemini_availability()
        
        # Check database connection
        db_available = True
        try:
            await db.execute("SELECT 1")
        except Exception:
            db_available = False
        
        # Check Telegram configuration
        telegram_configured = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        
        # Thai timezone for system status
        thai_tz = pytz.timezone('Asia/Bangkok')
        thai_time = datetime.now(thai_tz)
        
        return {
            "status": "ok",
            "ai_available": ai_available,
            "database_available": db_available,
            "telegram_configured": telegram_configured,
            "line_configured": bool(settings.LINE_CHANNEL_ACCESS_TOKEN),
            "timestamp": thai_time.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/force_bot_mode", summary="API สำหรับบังคับโหมดบอทสำหรับผู้ใช้")
async def force_bot_mode(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    """บังคับเปลี่ยนโหมดเป็นบอทและออกจาก live chat"""
    try:
        await set_live_chat_status(db, payload.user_id, False)
        await set_chat_mode(db, payload.user_id, 'bot')
        
        notification = "🤖 เปลี่ยนเป็นโหมดบอทอัตโนมัติแล้ว"
        await manager.broadcast({
            "type": "mode_changed", "userId": payload.user_id,
            "mode": "bot", "message": notification
        })
        
        return {"status": "ok", "mode": "bot"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))