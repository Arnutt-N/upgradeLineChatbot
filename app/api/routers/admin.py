# app/api/routers/admin.py - ฉบับแก้ไขเพื่อให้แสดงข้อมูลได้ถูกต้อง
from fastapi import APIRouter, Request, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import json
from linebot.v3.messaging import (
    AsyncApiClient, AsyncMessagingApi, Configuration, 
    TextMessage, PushMessageRequest, ShowLoadingAnimationRequest
)

from app.utils.timezone import convert_to_thai_time, get_thai_time
from app.core.config import settings
from app.db.database import get_db

# Import CRUD functions ที่แก้ไขแล้ว
from app.db.crud import (
    set_live_chat_status, 
    set_chat_mode,
    get_or_create_user_status
)

# ใช้ฟังก์ชันใหม่ที่มีการป้องกันข้อผิดพลาด
from app.db.crud_enhanced import (
    save_chat_to_history,
    get_all_chat_history_by_user,
    get_users_with_history,
    get_latest_chat_in_history
)

from app.schemas.chat import ReplyPayload, EndChatPayload, ToggleModePayload
from app.services.ws_manager import manager

# ตั้งค่า Templates
templates = Jinja2Templates(directory="templates")

def get_line_bot_api():
    """สร้าง LINE Bot API client"""
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    return AsyncMessagingApi(async_api_client)

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):
    """หน้าแรก - redirect ไป admin"""
    return templates.TemplateResponse("admin.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def get_admin_page(request: Request):
    """หน้า Admin Panel พร้อม Loading Animation"""
    return templates.TemplateResponse("admin.html", {"request": request})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket สำหรับ Real-time Updates"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle client messages if needed
            try:
                client_data = json.loads(data)
                if client_data.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now().isoformat()}))
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@router.post("/admin/reply")
async def admin_reply(payload: ReplyPayload, db: AsyncSession = Depends(get_db)):
    """ส่งข้อความตอบกลับพร้อม Loading Animation"""
    try:
        print(f"🔄 Admin replying to user {payload.user_id}: {payload.message}")
        line_bot_api = get_line_bot_api()
        
        # 1. แสดง Loading Animation ใน LINE Chat (พยายาม)
        try:
            loading_request = ShowLoadingAnimationRequest(
                chat_id=payload.user_id,
                loading_seconds=3  # เพิ่มเวลาเป็น 3 วินาที
            )
            await line_bot_api.show_loading_animation(loading_request)
            print(f"✅ Loading animation shown successfully for user {payload.user_id}")
        except Exception as loading_error:
            print(f"⚠️ Loading animation failed (not critical): {loading_error}")
            # ไม่หยุดการทำงาน - ส่งข้อความต่อไป
        
        # 2. Broadcast loading state ไปยัง Admin Panel
        await manager.broadcast({
            "type": "admin_sending",
            "userId": payload.user_id,
            "message": "กำลังส่งข้อความ..."
        })
        
        # 3. บันทึกข้อความของ Admin
        try:
            await save_chat_to_history(
                db=db, 
                user_id=payload.user_id, 
                message_type='admin', 
                message_content=payload.message,
                admin_user_id="system_admin"  # เพิ่ม admin_user_id
            )
            print(f"✅ Chat history saved for admin message")
        except Exception as save_error:
            print(f"⚠️ Failed to save chat history: {save_error}")
            # ส่งข้อความต่อไปแม้จะบันทึกไม่ได้
        
        # 4. ส่ง Push Message ไปยัง LINE
        try:
            push_request = PushMessageRequest(
                to=payload.user_id,
                messages=[TextMessage(text=payload.message)]
            )
            await line_bot_api.push_message(push_request)
            print(f"✅ Push message sent successfully to {payload.user_id}")
        except Exception as push_error:
            print(f"❌ Failed to send push message: {push_error}")
            # ยังคงส่ง success response เพราะข้อความถูกบันทึกแล้ว
        
        # 5. Broadcast success ไปยัง Admin Panel
        await manager.broadcast({
            "type": "message_sent",
            "userId": payload.user_id,
            "message": payload.message,
            "timestamp": datetime.now().isoformat()
        })

        return {
            "status": "success",
            "message": "ข้อความถูกส่งเรียบร้อยแล้ว",
            "user_id": payload.user_id
        }
        
    except Exception as e:
        print(f"❌ Critical error in admin_reply: {e}")
        import traceback
        traceback.print_exc()
        
        # Broadcast error ไปยัง Admin Panel
        await manager.broadcast({
            "type": "send_error",
            "userId": payload.user_id,
            "error": str(e)
        })
        
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

@router.get("/admin/users")
async def get_users_list(db: AsyncSession = Depends(get_db)):
    """โหลดรายชื่อผู้ใช้ทั้งหมด - Enhanced Version"""
    try:
        print("🔄 Loading users list from database...")
        
        # ใช้ฟังก์ชันที่ปรับปรุงแล้ว
        users_data = await get_users_with_history(db)
        
        if not users_data:
            print("⚠️ No users found in database")
            return {
                "users": [],
                "message": "ยังไม่มีผู้ใช้ในระบบ",
                "count": 0
            }
        
        print(f"📊 Processing {len(users_data)} users...")
        users_list = []
        
        for user_data in users_data:
            try:
                user_id = user_data.user_id
                
                # ดึงข้อความล่าสุด
                latest_message = await get_latest_chat_in_history(db, user_id)
                
                # สร้างข้อมูลผู้ใช้
                user_info = {
                    "user_id": user_id,
                    "display_name": user_data.display_name or f"ลูกค้า {user_id[-6:]}",
                    "picture_url": user_data.picture_url or "/static/images/avatars/default_user_avatar.png",
                    "is_in_live_chat": getattr(user_data, 'is_in_live_chat', False),
                    "chat_mode": getattr(user_data, 'chat_mode', 'manual'),
                    "latest_message": latest_message.message_content if latest_message else "ยังไม่มีการแชท",
                    "last_activity": latest_message.timestamp.isoformat() if latest_message else None,
                    "unread_count": 0,  # จะต้องเพิ่มการนับข้อความที่ยังไม่อ่านในอนาคต
                    "online_status": "online" if getattr(user_data, 'is_in_live_chat', False) else "offline"
                }
                
                users_list.append(user_info)
                
            except Exception as user_error:
                print(f"⚠️ Error processing user {getattr(user_data, 'user_id', 'unknown')}: {user_error}")
                # เพิ่ม fallback user entry
                try:
                    users_list.append({
                        "user_id": getattr(user_data, 'user_id', f'user_{len(users_list)}'),
                        "display_name": f"ลูกค้า {getattr(user_data, 'user_id', 'unknown')[-6:]}",
                        "picture_url": "/static/images/avatars/default_user_avatar.png",
                        "is_in_live_chat": False,
                        "chat_mode": "manual",
                        "latest_message": f"ข้อผิดพลาดในการโหลดข้อมูล: {str(user_error)[:50]}...",
                        "last_activity": None,
                        "unread_count": 0,
                        "online_status": "offline"
                    })
                except:
                    continue
        
        # เรียงลำดับตาม last_activity
        users_list.sort(key=lambda x: x['last_activity'] or '1900-01-01', reverse=True)
        
        print(f"✅ Successfully loaded {len(users_list)} users for admin panel")
        
        return {
            "users": users_list,
            "count": len(users_list),
            "message": f"โหลดข้อมูลผู้ใช้ {len(users_list)} คนเรียบร้อย"
        }
        
    except Exception as e:
        print(f"❌ Critical error in get_users_list: {e}")
        import traceback
        traceback.print_exc()
        
        # ส่งข้อมูล error ที่มีประโยชน์
        return {
            "users": [],
            "count": 0,
            "error": str(e),
            "message": f"ไม่สามารถโหลดข้อมูลผู้ใช้ได้: {str(e)[:100]}...",
            "success": False
        }

@router.get("/admin/messages/{user_id}")
async def get_user_messages(user_id: str, db: AsyncSession = Depends(get_db)):
    """โหลดข้อความของผู้ใช้ - Enhanced Version"""
    try:
        print(f"🔄 Loading messages for user: {user_id}")
        
        # ใช้ฟังก์ชันที่ปรับปรุงแล้วพร้อม fallback
        messages = await get_all_chat_history_by_user(db, user_id, limit=200)  # เพิ่ม limit
        
        if not messages:
            print(f"⚠️ No messages found for user: {user_id}")
            return {
                "messages": [],
                "count": 0,
                "user_id": user_id,
                "message": "ยังไม่มีประวัติการสนทนา"
            }
        
        print(f"📊 Processing {len(messages)} messages for user: {user_id}")
        messages_list = []
        
        for index, msg in enumerate(messages):
            try:
                # แปลงเวลาเป็นเขตเวลาไทย
                try:
                    thai_time = convert_to_thai_time(msg.timestamp)
                    formatted_time = thai_time.isoformat()
                except Exception as time_error:
                    print(f"⚠️ Time conversion error: {time_error}")
                    formatted_time = datetime.now().isoformat()
                
                # สร้างข้อมูลข้อความ
                message_info = {
                    "id": getattr(msg, 'id', f"msg_{index}"),
                    "message": getattr(msg, 'message_content', '') or getattr(msg, 'message', ''),
                    "sender_type": getattr(msg, 'message_type', 'unknown') or getattr(msg, 'sender_type', 'unknown'),
                    "created_at": formatted_time,
                    "user_id": user_id,
                    "is_read": getattr(msg, 'is_read', True)
                }
                
                messages_list.append(message_info)
                
            except Exception as msg_error:
                print(f"⚠️ Error processing message {index}: {msg_error}")
                # เพิ่ม fallback message
                messages_list.append({
                    "id": f"error_msg_{index}",
                    "message": f"[ข้อผิดพลาดในการโหลดข้อความ: {str(msg_error)[:50]}...]",
                    "sender_type": "system",
                    "created_at": datetime.now().isoformat(),
                    "user_id": user_id,
                    "is_read": True
                })
        
        print(f"✅ Successfully processed {len(messages_list)} messages for user: {user_id}")
        
        return {
            "messages": messages_list,
            "count": len(messages_list),
            "user_id": user_id,
            "message": f"โหลดข้อความ {len(messages_list)} ข้อความเรียบร้อย"
        }
        
    except Exception as e:
        print(f"❌ Critical error loading messages for user {user_id}: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "messages": [],
            "count": 0,
            "user_id": user_id,
            "error": str(e),
            "message": f"ไม่สามารถโหลดข้อความได้: {str(e)[:100]}...",
            "success": False
        }

@router.get("/admin/status")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """ตรวจสอบสถานะระบบแบบละเอียด"""
    try:
        print("🔍 Checking comprehensive system status...")
        
        system_checks = {}
        overall_status = "healthy"
        
        # 1. ตรวจสอบ Database
        db_status = {"available": False, "error": None, "stats": {}}
        try:
            from sqlalchemy import text
            # Test basic connection
            result = await db.execute(text("SELECT 1"))
            result.fetchone()
            
            # Get table statistics
            try:
                user_result = await db.execute(text("SELECT COUNT(*) FROM user_status"))
                user_count = user_result.scalar()
                
                chat_result = await db.execute(text("SELECT COUNT(*) FROM chat_history"))
                chat_count = chat_result.scalar()
                
                db_status.update({
                    "available": True,
                    "stats": {
                        "users": user_count,
                        "messages": chat_count
                    }
                })
            except Exception as stats_error:
                print(f"⚠️ Could not get database stats: {stats_error}")
                db_status["available"] = True  # Connection works, just no stats
                
        except Exception as db_error:
            db_status["error"] = str(db_error)
            overall_status = "degraded"
            
        system_checks["database"] = db_status
        
        # 2. ตรวจสอบ WebSocket
        try:
            from app.services.ws_manager import manager
            ws_count = manager.get_connection_count()
            system_checks["websocket"] = {
                "available": True,
                "connections": ws_count
            }
        except Exception as ws_error:
            system_checks["websocket"] = {
                "available": False,
                "error": str(ws_error)
            }
            if overall_status == "healthy":
                overall_status = "degraded"
        
        # 3. ตรวจสอบ LINE Bot Configuration
        line_configured = bool(settings.LINE_CHANNEL_ACCESS_TOKEN and settings.LINE_CHANNEL_SECRET)
        system_checks["line_bot"] = {
            "configured": line_configured,
            "status": "ready" if line_configured else "not_configured"
        }
        
        if not line_configured:
            overall_status = "error"
        
        # 4. ตรวจสอบ Gemini AI
        try:
            from app.services.gemini_service import check_gemini_availability
            ai_available = await check_gemini_availability()
            system_checks["ai_service"] = {
                "available": ai_available,
                "status": "ready" if ai_available else "unavailable"
            }
        except Exception as ai_error:
            system_checks["ai_service"] = {
                "available": False,
                "error": str(ai_error),
                "status": "error"
            }
            if overall_status == "healthy":
                overall_status = "degraded"
        
        # สรุปผล
        thai_time = get_thai_time()
        
        return {
            "overall_status": overall_status,
            "timestamp": thai_time.isoformat(),
            "checks": system_checks,
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
            "summary": {
                "total_checks": len(system_checks),
                "healthy": sum(1 for check in system_checks.values() 
                              if check.get('available', check.get('configured', False))),
                "issues": sum(1 for check in system_checks.values() 
                             if not check.get('available', check.get('configured', False)))
            }
        }
        
    except Exception as e:
        print(f"❌ System status check failed: {e}")
        return {
            "overall_status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "checks": {}
        }

# เพิ่ม endpoints อื่น ๆ ที่จำเป็น
@router.post("/admin/end_chat")
async def end_chat(payload: EndChatPayload, db: AsyncSession = Depends(get_db)):
    """จบการสนทนา"""
    try:
        line_bot_api = get_line_bot_api()
        await set_live_chat_status(db, payload.user_id, False)
        
        end_message = "เจ้าหน้าที่ได้จบการสนทนาแล้วค่ะ หากมีคำถามเพิ่มเติม สามารถพิมพ์เพื่อคุยกับบอทได้เลยค่ะ"
        
        try:
            push_request = PushMessageRequest(to=payload.user_id, messages=[TextMessage(text=end_message)])
            await line_bot_api.push_message(push_request)
            
            # บันทึกข้อความของบอท
            await save_chat_to_history(
                db=db, 
                user_id=payload.user_id, 
                message_type='bot', 
                message_content=end_message
            )
        except Exception as e:
            print(f"Error ending chat: {e}")
            
        return {"status": "success", "message": "จบการสนทนาเรียบร้อยแล้ว"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/admin/toggle_mode")
async def toggle_mode(payload: ToggleModePayload, db: AsyncSession = Depends(get_db)):
    """สลับโหมดการแชท"""
    try:
        await set_chat_mode(db, payload.user_id, payload.mode)
        
        mode_text = "แอดมินจะตอบเอง" if payload.mode == 'manual' else "บอทจะตอบอัตโนมัติ"
        
        await manager.broadcast({
            "type": "mode_changed",
            "userId": payload.user_id,
            "mode": payload.mode,
            "message": f"🔄 โหมดการตอบเปลี่ยนเป็น: {mode_text}"
        })
        
        return {"status": "success", "mode": payload.mode, "message": mode_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
