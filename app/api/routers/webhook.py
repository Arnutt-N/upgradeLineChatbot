# app/api/routers/webhook.py - Fixed version
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent, TextMessageContent, ImageMessageContent, FileMessageContent,
    FollowEvent, UnfollowEvent, JoinEvent, LeaveEvent, PostbackEvent
)

from app.core.config import settings
from app.db.database import get_db
from app.services.line_handler_enhanced import (
    handle_follow_event, handle_unfollow_event, handle_message_enhanced,
    handle_image_message_enhanced, handle_file_message_enhanced
)
from app.db.crud_enhanced import log_system_event

# ตั้งค่า LINE SDK - สร้างเมื่อต้องใช้
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def get_line_bot_api():
    """สร้าง LINE Bot API client"""
    configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
    async_api_client = AsyncApiClient(configuration)
    return AsyncMessagingApi(async_api_client)

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """Simple health check endpoint"""
    return {"status": "ok", "message": "Webhook server is running"}

@router.get("/webhook", summary="Webhook Health Check")
async def webhook_health():
    """GET endpoint for webhook testing"""
    return {"status": "ok", "message": "Webhook endpoint is ready"}

@router.post("/webhook", summary="รับ Events จาก LINE Platform - Fixed")
async def line_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """LINE webhook endpoint with proper error handling"""
    try:
        # Validate LINE configuration first
        try:
            settings.validate_required_settings()
        except ValueError as e:
            print(f"Configuration error: {e}")
            return {"status": "error", "message": "LINE Bot not configured properly"}
        
        signature = request.headers.get('X-Line-Signature')
        body = await request.body()
        
        # บันทึก request info สำหรับ debugging
        request_id = f"req_{id(request)}"
        
        # ตรวจสอบว่ามี signature และ body ไหม
        if not signature:
            await log_system_event(
                db=db,
                level="warning",
                category="line_webhook",
                subcategory="missing_signature",
                message="No X-Line-Signature header found",
                request_id=request_id
            )
            return {"status": "ok", "message": "No signature provided"}
        
        if not body:
            await log_system_event(
                db=db,
                level="warning", 
                category="line_webhook",
                subcategory="empty_body",
                message="Empty request body",
                request_id=request_id
            )
            return {"status": "ok", "message": "Empty body"}
        
        try:
            # Decode body เป็น string
            body_str = body.decode('utf-8')
            print(f"Received webhook body: {body_str[:200]}...")  # Log first 200 chars
            
            # Parse events
            events = parser.parse(body_str, signature)
            print(f"Parsed {len(events)} events")
            
            await log_system_event(
                db=db,
                level="info",
                category="line_webhook",
                subcategory="events_received",
                message=f"Received {len(events)} events",
                details={"event_count": len(events), "body_size": len(body_str)},
                request_id=request_id
            )
            
        except InvalidSignatureError as e:
            print(f"Invalid signature error: {e}")
            await log_system_event(
                db=db,
                level="error",
                category="line_webhook",
                subcategory="invalid_signature",
                message=f"Invalid signature: {str(e)}",
                request_id=request_id
            )
            raise HTTPException(status_code=400, detail="Invalid signature.")
            
        except Exception as e:
            print(f"Parser error: {type(e).__name__}: {e}")
            await log_system_event(
                db=db,
                level="error",
                category="line_webhook", 
                subcategory="parse_error",
                message=f"Parse error: {str(e)}",
                request_id=request_id
            )
            return {"status": "error", "message": f"Parse error: {e}"}
        
        line_bot_api = get_line_bot_api()
        
        # Process events
        processed_events = 0
        failed_events = 0
        
        for event in events:
            try:
                event_type = type(event).__name__
                print(f"Processing event type: {event_type}")
                
                if isinstance(event, MessageEvent):
                    # Use the enhanced message handler for different message types
                    try:
                        if isinstance(event.message, TextMessageContent):
                            await handle_message_enhanced(event, db, line_bot_api)
                        elif isinstance(event.message, ImageMessageContent):
                            await handle_image_message_enhanced(event, db, line_bot_api)
                        elif isinstance(event.message, FileMessageContent):
                            await handle_file_message_enhanced(event, db, line_bot_api)
                        else:
                            # Handle other message types with text handler as fallback
                            await handle_message_enhanced(event, db, line_bot_api)
                        
                        processed_events += 1
                    except Exception as e:
                        print(f"Error processing message event: {e}")
                        await log_system_event(
                            db=db,
                            level="error",
                            category="line_webhook",
                            subcategory="message_handler_error",
                            message=f"Message handler error: {str(e)}",
                            details={"event_type": type(event.message).__name__},
                            request_id=request_id
                        )
                        failed_events += 1
                    
                elif isinstance(event, FollowEvent):
                    # Friend follow events
                    await handle_follow_event(event, db, line_bot_api)
                    processed_events += 1
                    
                elif isinstance(event, UnfollowEvent):
                    # Friend unfollow events
                    await handle_unfollow_event(event, db, line_bot_api)
                    processed_events += 1
                    
                elif isinstance(event, JoinEvent):
                    # Bot joined group/room
                    await log_system_event(
                        db=db,
                        level="info",
                        category="line_webhook",
                        subcategory="join_event",
                        message="Bot joined group/room",
                        details={"event_type": event_type},
                        request_id=request_id
                    )
                    processed_events += 1
                    
                elif isinstance(event, LeaveEvent):
                    # Bot left group/room
                    await log_system_event(
                        db=db,
                        level="info",
                        category="line_webhook",
                        subcategory="leave_event", 
                        message="Bot left group/room",
                        details={"event_type": event_type},
                        request_id=request_id
                    )
                    processed_events += 1
                    
                elif isinstance(event, PostbackEvent):
                    # Postback events (buttons, quick replies)
                    await log_system_event(
                        db=db,
                        level="info",
                        category="line_webhook",
                        subcategory="postback_event",
                        message="Postback event received",
                        details={"event_type": event_type, "data": event.postback.data},
                        request_id=request_id
                    )
                    processed_events += 1
                    
                else:
                    # Unknown event types
                    await log_system_event(
                        db=db,
                        level="warning",
                        category="line_webhook",
                        subcategory="unknown_event",
                        message=f"Unknown event type: {event_type}",
                        details={"event_type": event_type},
                        request_id=request_id
                    )
                    
            except Exception as e:
                print(f"Error handling event: {type(e).__name__}: {e}")
                failed_events += 1
                
                await log_system_event(
                    db=db,
                    level="error",
                    category="line_webhook",
                    subcategory="event_processing_error",
                    message=f"Error handling {type(event).__name__}: {str(e)}",
                    details={"event_type": type(event).__name__, "error": str(e)},
                    request_id=request_id
                )
        
        # สรุปผลการประมวลผล
        await log_system_event(
            db=db,
            level="info",
            category="line_webhook",
            subcategory="processing_complete",
            message="Webhook processing completed",
            details={
                "total_events": len(events),
                "processed_events": processed_events,
                "failed_events": failed_events
            },
            request_id=request_id
        )
        
        return {
            "status": "ok", 
            "total_events": len(events),
            "processed": processed_events,
            "failed": failed_events
        }
        
    except Exception as e:
        # Catch any unhandled errors to prevent 500 status
        print(f"Webhook error: {type(e).__name__}: {e}")
        try:
            await log_system_event(
                db=db,
                level="error",
                category="line_webhook",
                subcategory="unhandled_error",
                message=f"Unhandled webhook error: {str(e)}",
                details={"error_type": type(e).__name__, "error": str(e)}
            )
        except:
            pass  # Even logging failed, but we still need to return 200
        
        return {"status": "error", "message": "Internal error occurred"}