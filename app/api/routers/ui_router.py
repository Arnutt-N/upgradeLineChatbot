# UI Router for serving HTML templates
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.ws_manager import manager

router = APIRouter(prefix="/ui", tags=["UI Templates"])
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_overview(request: Request):
    """Enhanced Admin Dashboard"""
    return templates.TemplateResponse("dashboard/overview.html", {"request": request})

@router.get("/analytics", response_class=HTMLResponse) 
async def analytics_dashboard(request: Request):
    """Analytics and History Dashboard"""
    return templates.TemplateResponse("history/chat_history.html", {"request": request})

@router.get("/chat-history", response_class=HTMLResponse)
async def chat_history_page(request: Request):
    """Chat History Page"""
    return templates.TemplateResponse("history/chat_history.html", {"request": request})

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # You can add logic here to handle incoming messages from the WebSocket if needed
            # For now, we are primarily using it for server-to-client communication
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Export router
__all__ = ["router"]
