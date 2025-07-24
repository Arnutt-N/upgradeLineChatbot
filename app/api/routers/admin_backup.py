# app/api/routers/admin.py (ฉบับแก้ไข)
from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from linebot.v3.messaging import (
    AsyncApiClient, AsyncMessagingApi, Configuration, 
    TextMessage, PushMessageRequest, ShowLoadingAnimationRequest
)

from app.utils.timezone import convert_to_thai_time, get_thai_time

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
        
        # 1. แสดง loading animation with graceful fallback
        loading_success = False
        try:
            loading_request = ShowLoadingAnimationRequest(
                chat_id=payload.user_id,
                loading_seconds=2
            )
            await line_bot_api.show_loading_animation(loading_request)
            loading_success = True
            print(f"✅ Admin loading animation shown for user {payload.user_id}")
        except Exception as e:
            print(f"⚠️  Admin loading animation failed for user {payload.user_id}: {e}")
            # Continue without breaking the flow
        
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
        print("Starting to load users list...")
        
        # ใช้ฟังก์ชันใหม่ในการดึงรายชื่อผู้ใช้
        users_data = await get_users_with_history(db)
        users_list = []
        
        if not users_data:
            print("No users found in database")
            return {"users": []}
        
        print(f"Processing {len(users_data)} users...")
        
        for user_data in users_data:
            try:
                user_id = user_data.user_id
                
                # ใช้ฟังก์ชันใหม่ในการดึงข้อความล่าสุด
                latest_message = await get_latest_chat_in_history(db, user_id)
                
                user_info = {
                    "user_id": user_id,
                    "display_name": user_data.display_name or f"Customer {user_id[-6:]}",
                    "picture_url": user_data.picture_url,
                    "is_in_live_chat": getattr(user_data, 'is_in_live_chat', False),
                    "chat_mode": getattr(user_data, 'chat_mode', 'manual'),
                    "latest_message": latest_message.message_content if latest_message else "ยังไม่มีการแชท",
                    "last_activity": latest_message.timestamp.isoformat() if latest_message else None
                }
                
                users_list.append(user_info)
                
            except Exception as user_error:
                print(f"Error processing user {getattr(user_data, 'user_id', 'unknown')}: {user_error}")
                continue
        
        print(f"Successfully processed {len(users_list)} users for admin panel")
        return {"users": users_list}
        
    except Exception as e:
        print(f"Critical error in get_users_list: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load users: {str(e)}")

@router.get("/admin/messages/{user_id}", summary="API สำหรับโหลดข้อความของผู้ใช้")
async def get_user_messages(user_id: str, db: AsyncSession = Depends(get_db)):
    try:
        print(f"Loading messages for user: {user_id}")
        
        # ใช้ฟังก์ชันใหม่ในการดึงประวัติแชท
        messages = await get_all_chat_history_by_user(db, user_id)
        messages_list = []
        
        if not messages:
            print(f"No messages found for user: {user_id}")
            return {"messages": []}
        
        print(f"Processing {len(messages)} messages for user: {user_id}")
        
        for msg in messages:
            try:
                # Convert timestamp to Thai timezone using utility
                thai_time = convert_to_thai_time(msg.timestamp)
                
                message_info = {
                    "id": getattr(msg, 'id', 'unknown'),
                    "message": getattr(msg, 'message_content', ''),
                    "sender_type": getattr(msg, 'message_type', 'unknown'),
                    "created_at": thai_time.isoformat()
                }
                
                messages_list.append(message_info)
                
            except Exception as msg_error:
                print(f"Error processing message {getattr(msg, 'id', 'unknown')}: {msg_error}")
                # Add fallback message info
                messages_list.append({
                    "id": getattr(msg, 'id', f"msg_{len(messages_list)}"),
                    "message": f"Error loading message: {str(msg_error)}",
                    "sender_type": "system",
                    "created_at": datetime.now().isoformat()
                })
        
        print(f"Successfully processed {len(messages_list)} messages for user: {user_id}")
        return {"messages": messages_list}
        
    except Exception as e:
        print(f"Critical error in get_user_messages for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to load messages for user {user_id}: {str(e)}")

@router.get("/admin/status", summary="API สำหรับตรวจสอบสถานะระบบ")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """ตรวจสอบสถานะระบบและการเชื่อมต่อ - Enhanced Version"""
    system_checks = {}
    overall_status = "ok"
    
    try:
        print("🔍 Starting comprehensive system status check...")
        
        # Check Gemini AI availability
        print("Checking Gemini AI service...")
        ai_available = False
        ai_error = None
        ai_details = {}
        try:
            from app.services.gemini_service import check_gemini_availability, get_gemini_status
            ai_available = await check_gemini_availability()
            ai_details = get_gemini_status()
        except Exception as e:
            ai_error = str(e)
            overall_status = "degraded"
        
        system_checks["gemini_ai"] = {
            "available": ai_available,
            "error": ai_error,
            "details": ai_details
        }
        
        # Check database connection with detailed info
        print("Checking database connection...")
        db_available = True
        db_error = None
        db_stats = {}
        try:
            from sqlalchemy import text
            
            # Basic connection test
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get user count
            user_result = await db.execute(text("SELECT COUNT(*) FROM user_status"))
            user_count = user_result.scalar()
            
            # Get message counts from both tables
            try:
                old_msg_result = await db.execute(text("SELECT COUNT(*) FROM chat_messages"))
                old_message_count = old_msg_result.scalar()
            except:
                old_message_count = 0
                
            try:
                new_msg_result = await db.execute(text("SELECT COUNT(*) FROM chat_history"))
                new_message_count = new_msg_result.scalar()
            except:
                new_message_count = 0
            
            db_stats = {
                "user_count": user_count,
                "old_messages": old_message_count,
                "new_messages": new_message_count,
                "total_messages": old_message_count + new_message_count
            }
            
        except Exception as e:
            db_available = False
            db_error = str(e)
            overall_status = "error"
        
        system_checks["database"] = {
            "available": db_available,
            "error": db_error,
            "stats": db_stats
        }
        
        # Check WebSocket connections
        print("Checking WebSocket connections...")
        try:
            from app.services.ws_manager import manager
            ws_connections = manager.get_connection_count()
            system_checks["websocket"] = {
                "available": True,
                "active_connections": ws_connections
            }
        except Exception as e:
            system_checks["websocket"] = {
                "available": False,
                "error": str(e)
            }
            if overall_status == "ok":
                overall_status = "degraded"
        
        # Check LINE Bot configuration
        print("Checking LINE Bot configuration...")
        line_configured = bool(settings.LINE_CHANNEL_ACCESS_TOKEN and settings.LINE_CHANNEL_SECRET)
        system_checks["line_bot"] = {
            "configured": line_configured,
            "has_access_token": bool(settings.LINE_CHANNEL_ACCESS_TOKEN),
            "has_channel_secret": bool(settings.LINE_CHANNEL_SECRET)
        }
        
        if not line_configured:
            overall_status = "error"
        
        # Check Telegram configuration
        print("Checking Telegram configuration...")
        telegram_configured = bool(settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID)
        system_checks["telegram"] = {
            "configured": telegram_configured,
            "has_bot_token": bool(settings.TELEGRAM_BOT_TOKEN),
            "has_chat_id": bool(settings.TELEGRAM_CHAT_ID)
        }
        
        # Get Thai timezone for timestamp
        thai_time = None
        try:
            thai_time = get_thai_time()
        except Exception as e:
            system_checks["timezone"] = {"error": str(e)}
            from datetime import datetime
            thai_time = datetime.now()
        
        # Compile final response
        response_data = {
            "overall_status": overall_status,
            "timestamp": thai_time.isoformat(),
            "checks": system_checks,
            "environment": settings.ENVIRONMENT,
            "app_version": settings.APP_VERSION,
            "summary": {
                "total_checks": len(system_checks),
                "passed": sum(1 for check in system_checks.values() 
                             if check.get('available', check.get('configured', False))),
                "warnings": 1 if overall_status == "degraded" else 0,
                "errors": 1 if overall_status == "error" else 0
            }
        }
        
        print(f"✅ System status check completed: {overall_status}")
        return response_data
        
    except Exception as e:
        print(f"❌ Critical system status check failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "overall_status": "critical_error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "checks": system_checks
        }

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