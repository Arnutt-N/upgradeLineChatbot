# app/api/routers/admin.py
from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration, TextMessage, PushMessageRequest

from app.core.config import settings
from app.db.database import get_db
from app.db.crud import (
    save_chat_message, 
    set_live_chat_status, 
    set_chat_mode,
    get_chat_messages,
    get_users_with_messages,
    get_or_create_user_status
)
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
    """
    รับข้อความจาก Admin UI, บันทึกลง DB,
    ส่ง Push Message ไปหาผู้ใช้, และ Broadcast ไปยัง Admin UI อื่นๆ
    """
    try:
        line_bot_api = get_line_bot_api()
        
        # 1. แสดง loading animation ให้ผู้ใช้เห็นว่าแอดมินกำลังพิมพ์
        try:
            from linebot.v3.messaging import ShowLoadingAnimationRequest
            loading_request = ShowLoadingAnimationRequest(
                chat_id=payload.user_id,
                loading_seconds=3  # แสดง 3 วินาที
            )
            await line_bot_api.show_loading_animation(loading_request)
        except Exception as e:
            print(f"Error showing loading animation: {e}")
        
        # 2. บันทึกข้อความของแอดมินลง DB
        await save_chat_message(db, payload.user_id, 'admin', payload.message)
        
        # 3. ส่ง Push Message ไปยังผู้ใช้ผ่าน LINE API
        try:
            from linebot.v3.messaging import PushMessageRequest
            push_request = PushMessageRequest(
                to=payload.user_id,
                messages=[TextMessage(text=payload.message)]
            )
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE push message: {e}")
        
        # 3. Broadcast ข้อความของแอดมินไปยังทุก Admin UI ที่เชื่อมต่ออยู่ (แต่ไม่รวมผู้ส่ง)
        # await manager.broadcast({
        #     "type": "admin_reply",
        #     "userId": payload.user_id,
        #     "message": payload.message
        # })
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/end_chat", summary="API สำหรับจบการสนทนา")
async def end_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    """ตั้งค่าสถานะผู้ใช้กลับเป็นโหมดบอท"""
    try:
        line_bot_api = get_line_bot_api()
        
        await set_live_chat_status(db, payload.user_id, False)
        
        # ส่งข้อความแจ้งผู้ใช้ว่าแอดมินจบการสนทนาแล้ว
        end_message = "เจ้าหน้าที่ได้จบการสนทนาแล้วค่ะ หากมีคำถามเพิ่มเติม สามารถพิมพ์เพื่อคุยกับบอทได้เลยค่ะ"
        
        try:
            push_request = PushMessageRequest(
                to=payload.user_id,
                messages=[TextMessage(text=end_message)]
            )
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE end chat message: {e}")
            
        await save_chat_message(db, payload.user_id, 'bot', end_message)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/toggle_mode", summary="API สำหรับสลับโหมดการแชท")
async def toggle_mode(payload: ToggleModePayload, db: AsyncSession = Depends(get_db)):
    """สลับโหมดการแชทระหว่าง manual และ auto"""
    try:
        await set_chat_mode(db, payload.user_id, payload.mode)
        
        # แจ้งผู้ใช้ว่าโหมดเปลี่ยน
        mode_text = "แอดมินจะตอบเอง" if payload.mode == 'manual' else "บอทจะตอบอัตโนมัติ"
        notification = f"🔄 โหมดการตอบเปลี่ยนเป็น: {mode_text}"
        
        # ส่งการแจ้งเตือนไปยัง Admin UI
        await manager.broadcast({
            "type": "mode_changed",
            "userId": payload.user_id,
            "mode": payload.mode,
            "message": notification
        })
        
        return {"status": "ok", "mode": payload.mode}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/restart_chat", summary="API สำหรับเริ่มการสนทนาใหม่")
async def restart_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    """เริ่มการสนทนาใหม่ - เปลี่ยนสถานะกลับเป็น live chat"""
    try:
        await set_live_chat_status(db, payload.user_id, True)
        
        # ส่งข้อความแจ้งผู้ใช้ว่าเริ่มการสนทนาใหม่แล้ว
        restart_message = "🟢 เจ้าหน้าที่พร้อมให้บริการแล้วค่ะ สามารถสอบถามได้เลยค่ะ"
        
        try:
            push_request = PushMessageRequest(
                to=payload.user_id,
                messages=[TextMessage(text=restart_message)]
            )
            await line_bot_api.push_message(push_request)
        except Exception as e:
            print(f"Error sending LINE restart message: {e}")
            
        await save_chat_message(db, payload.user_id, 'bot', restart_message)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/users", summary="API สำหรับโหลดรายการผู้ใช้ที่มีประวัติแชท")
async def get_users_list(db: AsyncSession = Depends(get_db)):
    """โหลดรายการผู้ใช้ทั้งหมดที่มีประวัติแชท"""
    try:
        from app.db.crud import get_users_with_messages, get_latest_message
        
        users_data = await get_users_with_messages(db)
        users_list = []
        
        for user_data in users_data:
            user_id = user_data.user_id
            display_name = user_data.display_name
            picture_url = user_data.picture_url
            is_in_live_chat = user_data.is_in_live_chat
            chat_mode = user_data.chat_mode
            
            # โหลดข้อความล่าสุด
            latest_message = await get_latest_message(db, user_id)
            
            users_list.append({
                "user_id": user_id,
                "display_name": display_name or f"Customer {user_id[-6:]}",  # ใช้ชื่อจากฐานข้อมูล
                "picture_url": picture_url,  # ส่ง picture URL ไปด้วย
                "is_in_live_chat": is_in_live_chat,
                "chat_mode": chat_mode,
                "latest_message": latest_message.message if latest_message else "ไม่มีข้อความ",
                "last_activity": latest_message.created_at.isoformat() if latest_message else None
            })
        
        return {"users": users_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/admin/messages/{user_id}", summary="API สำหรับโหลดข้อความของผู้ใช้")
async def get_user_messages(user_id: str, db: AsyncSession = Depends(get_db)):
    """โหลดข้อความทั้งหมดของผู้ใช้คนหนึ่ง"""
    try:
        from app.db.crud import get_chat_messages
        
        messages = await get_chat_messages(db, user_id)
        messages_list = []
        
        for msg in messages:
            messages_list.append({
                "id": msg.id,
                "message": msg.message,
                "sender_type": msg.sender_type,
                "created_at": msg.created_at.isoformat()
            })
        
        return {"messages": messages_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
