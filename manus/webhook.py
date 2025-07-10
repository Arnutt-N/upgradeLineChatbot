# app/api/routers/webhook.py
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from linebot.v3.webhook import WebhookParser
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

from app.core.config import settings
from app.db.database import get_db
from app.services.line_handler import handle_message

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

@router.get("/webhook/debug", summary="Debug Webhook Headers")
async def debug_webhook(request: Request):
    """Debug endpoint to see headers"""
    return {
        "headers": dict(request.headers),
        "method": request.method,
        "url": str(request.url)
    }

@router.post("/webhook", summary="รับ Events จาก LINE Platform")
async def line_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    
    # ตรวจสอบว่ามี signature และ body ไหม
    if not signature:
        print("Warning: No X-Line-Signature header found")
        return {"status": "ok", "message": "No signature provided"}
    
    if not body:
        print("Warning: Empty request body")
        return {"status": "ok", "message": "Empty body"}
    
    try:
        # Decode body เป็น string
        body_str = body.decode('utf-8')
        print(f"Received webhook body: {body_str[:200]}...")  # Log first 200 chars
        
        # Parse events
        events = parser.parse(body_str, signature)
        print(f"Parsed {len(events)} events")
        
    except InvalidSignatureError as e:
        print(f"Invalid signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature.")
    except Exception as e:
        print(f"Parser error: {type(e).__name__}: {e}")
        return {"status": "error", "message": f"Parse error: {e}"}
    
    line_bot_api = get_line_bot_api()
    
    # Process events
    for event in events:
        try:
            print(f"Processing event type: {type(event).__name__}")
            if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
                await handle_message(event, db, line_bot_api)
        except Exception as e:
            print(f"Error handling event: {type(e).__name__}: {e}")
    
    return {"status": "ok", "processed": len(events)}
