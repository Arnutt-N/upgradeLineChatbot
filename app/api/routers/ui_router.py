# UI Router for serving HTML templates
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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

# Export router
__all__ = ["router"]
