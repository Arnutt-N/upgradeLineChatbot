# main.py
import os
import uvicorn
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# --- นำเข้าส่วนต่างๆ ของโปรเจกต์ ---
from database import async_engine, Base, AsyncSessionLocal
import database as db_models
from live_chat import manager # Import a connection manager

# --- นำเข้าส่วนของ LINE SDK ---
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient, AsyncMessagingApi, Configuration, TextMessage
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

# --- 1. โหลดค่าจาก .env และตั้งค่าพื้นฐาน ---
load_dotenv()

app = FastAPI(
    title="LINE Bot with Full Live Chat System",
    version="1.3.0"
)

# ตั้งค่าสำหรับ Templates (เพื่อแสดงหน้า admin.html)
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def on_startup():
    print("Application startup: Creating database and tables...")
    await db_models.create_db_and_tables()
    print("Database and tables created successfully.")

# --- Credentials ---
# (เหมือนเดิม)
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# --- LINE SDK Instances ---
# (เหมือนเดิม)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)
parser = WebhookParser(CHANNEL_SECRET)

# --- 2. Database Dependency ---
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# --- 3. ฟังก์ชันจัดการฐานข้อมูล (CRUD) ---
# (เหมือนเดิม)
async def get_or_create_user_status(db: AsyncSession, user_id: str):
    result = await db.execute(select(db_models.UserStatus).filter(db_models.UserStatus.user_id == user_id))
    user_status = result.scalar_one_or_none()
    if not user_status:
        user_status = db_models.UserStatus(user_id=user_id, is_in_live_chat=False)
        db.add(user_status)
        await db.commit()
        await db.refresh(user_status)
    return user_status

async def set_live_chat_status(db: AsyncSession, user_id: str, status: bool):
    user_status = await get_or_create_user_status(db, user_id)
    user_status.is_in_live_chat = status
    await db.commit()
    return user_status

async def save_chat_message(db: AsyncSession, user_id: str, sender_type: str, message: str):
    new_message = db_models.ChatMessage(user_id=user_id, sender_type=sender_type, message=message)
    db.add(new_message)
    await db.commit()

# --- 4. ฟังก์ชันจัดการ Logic และ API ---
async def send_telegram_alert(message: str):
    # (เหมือนเดิม)
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    async with httpx.AsyncClient() as client:
        try:
            await client.get(api_url, params=params)
        except Exception as e:
            print(f"Error sending Telegram alert: {e}")

async def handle_message(event: MessageEvent, db: AsyncSession):
    user_id = event.source.user_id
    reply_token = event.reply_token
    message_text = event.message.text

    user_status = await get_or_create_user_status(db, user_id)

    if user_status.is_in_live_chat:
        # อยู่ในโหมด Live Chat: ส่งข้อความไปหน้า Admin UI ผ่าน WebSocket
        await save_chat_message(db, user_id, 'user', message_text)
        await manager.broadcast({
            "type": "new_message",
            "userId": user_id,
            "message": message_text
        })
    else:
        # อยู่ในโหมดบอท
        await save_chat_message(db, user_id, 'user', message_text)
        if "คุยกับแอดมิน" in message_text or "ติดต่อเจ้าหน้าที่" in message_text:
            await set_live_chat_status(db, user_id, True)
            response_text = "รับทราบค่ะ กำลังโอนสายไปยังเจ้าหน้าที่ รอสักครู่นะคะ..."
            await save_chat_message(db, user_id, 'bot', response_text)
            await line_bot_api.reply_message(reply_token, [TextMessage(text=response_text)])
            alert_message = f"🚨 *Human Handoff Request* 🚨\n\n*จาก:* `{user_id}`"
            await send_telegram_alert(alert_message)
            # แจ้งหน้า UI ว่ามี user ใหม่เข้ามา
            await manager.broadcast({
                "type": "new_message",
                "userId": user_id,
                "message": message_text # ส่งข้อความแรกไปด้วย
            })
        else:
            # โหมดบอทปกติ
            response_text = f"โหมดบอท: คุณส่งข้อความว่า '{message_text}'"
            await save_chat_message(db, user_id, 'bot', response_text)
            await line_bot_api.reply_message(reply_token, [TextMessage(text=response_text)])

# --- 5. Endpoints ---

# Webhook Endpoint (เหมือนเดิม)
@app.post("/webhook", summary="รับ Events จาก LINE Platform")
async def line_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    try:
        events = parser.parse(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            await handle_message(event, db)
    return 'OK'

# --- Admin Live Chat Endpoints ---

@app.get("/admin", response_class=HTMLResponse, summary="แสดงหน้า Live Chat สำหรับแอดมิน")
async def get_admin_page(request: Request):
    """Endpoint สำหรับแสดงไฟล์ admin.html"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Endpoint สำหรับ WebSocket ที่หน้า Admin UI จะเชื่อมต่อเข้ามา"""
    await manager.connect(websocket)
    try:
        while True:
            # รอรับข้อมูล (แต่ในเคสนี้เราใช้สำหรับส่งออกอย่างเดียว)
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

from pydantic import BaseModel

class ReplyPayload(BaseModel):
    user_id: str
    message: str

@app.post("/admin/reply", summary="API สำหรับแอดมินส่งข้อความตอบกลับ")
async def admin_reply(payload: ReplyPayload, db: AsyncSession = Depends(get_db)):
    """
    รับข้อความจาก Admin UI, บันทึกลง DB,
    ส่ง Push Message ไปหาผู้ใช้, และ Broadcast ไปยัง Admin UI อื่นๆ
    """
    try:
        # 1. บันทึกข้อความของแอดมินลง DB
        await save_chat_message(db, payload.user_id, 'admin', payload.message)
        
        # 2. ส่ง Push Message ไปยังผู้ใช้ผ่าน LINE API
        await line_bot_api.push_message(payload.user_id, [TextMessage(text=payload.message)])
        
        # 3. Broadcast ข้อความของแอดมินไปยังทุก Admin UI ที่เชื่อมต่ออยู่
        await manager.broadcast({
            "type": "admin_reply",
            "userId": payload.user_id,
            "message": payload.message
        })
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class EndChatPayload(BaseModel):
    user_id: str

@app.post("/admin/end_chat", summary="API สำหรับจบการสนทนา")
async def end_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    """ตั้งค่าสถานะผู้ใช้กลับเป็นโหมดบอท"""
    try:
        await set_live_chat_status(db, payload.user_id, False)
        
        # ส่งข้อความแจ้งผู้ใช้ว่าแอดมินจบการสนทนาแล้ว
        end_message = "เจ้าหน้าที่ได้จบการสนทนาแล้วค่ะ หากมีคำถามเพิ่มเติม สามารถพิมพ์เพื่อคุยกับบอทได้เลยค่ะ"
        await line_bot_api.push_message(payload.user_id, [TextMessage(text=end_message)])
        await save_chat_message(db, payload.user_id, 'bot', end_message)

        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- 6. ส่วนสำหรับรัน Server ---
if __name__ == "__main__":
    print("Starting server...")
    print("Admin Live Chat UI available at http://127.0.0.1:8000/admin")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
