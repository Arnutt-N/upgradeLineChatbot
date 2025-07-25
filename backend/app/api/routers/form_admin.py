# app/api/routers/form_admin.py
from fastapi import APIRouter, Request, HTTPException, Depends, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.config import settings
from app.db.database import get_db
from app.db.crud_forms import get_dashboard_stats, get_form_submissions, get_form_submission
from app.schemas.forms import FormType, FormStatus
from app.schemas.auth import LoginRequest, LoginResponse, SessionInfo
from app.auth.auth import authenticate_user, create_access_token, get_current_user, logout_user, get_session_info

# Templates สำหรับ Form Admin
templates = Jinja2Templates(directory="../frontend/templates")

router = APIRouter(prefix="/form-admin", tags=["Forms Admin"])

# === Authentication Endpoints ===

@router.get("/login", response_class=HTMLResponse, summary="Login Page")
async def login_page(request: Request):
    """หน้า Login สำหรับ Forms Admin"""
    return templates.TemplateResponse(
        "form_admin/login.html",
        {"request": request, "title": "เข้าสู่ระบบ"}
    )

@router.post("/api/login", summary="Login API")
async def login(login_data: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """API สำหรับเข้าสู่ระบบ"""
    try:
        user = await authenticate_user(db, login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token = create_access_token(user)
        
        # Set cookie (optional, for web interface)
        response.set_cookie(
            key="access_token",
            value=access_token,
            max_age=8 * 60 * 60,  # 8 hours
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        
        return LoginResponse(
            access_token=access_token,
            user_info={
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role
            },
            message="Login successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/api/logout", summary="Logout API")
async def logout(request: Request, response: Response):
    """API สำหรับออกจากระบบ"""
    try:
        # Get token from cookie
        token = request.cookies.get("access_token")
        
        if token:
            logout_user(token)
        
        # Clear cookie
        response.delete_cookie("access_token")
        
        return {"message": "Logout successful"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Logout failed: {str(e)}"
        )

@router.get("/api/session", summary="Session Info")
async def session_info(current_user = Depends(get_current_user)):
    """ข้อมูลเซสชันปัจจุบัน"""
    session_data = get_session_info()
    
    return SessionInfo(
        active_sessions=session_data["active_sessions"],
        current_user={
            "id": current_user.id,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active
        }
    )

@router.get("/", response_class=HTMLResponse, summary="Forms Admin Dashboard")
async def forms_admin_dashboard(
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    """หน้า Dashboard หลักของ Forms Admin (ตรวจสอบ authentication)"""
    try:
        # Try to get current user (this will raise HTTPException if not authenticated)
        from app.auth.auth import get_current_user
        current_user = await get_current_user(request, None, db)
        
        # ดึงสถิติจริงจาก database
        try:
            stats = await get_dashboard_stats(db)
        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            stats = {
                "total_today": 0,
                "pending_count": 0,
                "processing_count": 0, 
                "completed_count": 0,
                "rejected_count": 0,
                "total_count": 0
            }
        
        return templates.TemplateResponse(
            "form_admin/dashboard.html", 
            {
                "request": request, 
                "title": "Forms Admin Dashboard",
                "stats": stats,
                "current_user": current_user
            }
        )
        
    except HTTPException:
        # Not authenticated, redirect to login
        return RedirectResponse(url="/form-admin/login", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect(request: Request):
    """Redirect to main dashboard"""
    return templates.TemplateResponse(
        "form_admin/dashboard.html",
        {"request": request, "title": "Forms Admin Dashboard"}
    )

# === KP7 Forms Management ===
@router.get("/forms/kp7", response_class=HTMLResponse, summary="จัดการคำขอ ก.พ. 7")
async def kp7_forms_page(request: Request, db: AsyncSession = Depends(get_db)):
    """หน้าจัดการคำขอ ก.พ. 7 (ต้อง login)"""
    try:
        from app.auth.auth import get_current_user
        current_user = await get_current_user(request, None, db)
        
        return templates.TemplateResponse(
            "form_admin/kp7_forms.html",
            {
                "request": request, 
                "title": "จัดการคำขอ ก.พ. 7",
                "current_user": current_user
            }
        )
    except HTTPException:
        return RedirectResponse(url="/form-admin/login", status_code=302)

@router.get("/api/forms/kp7", summary="API รายการคำขอ ก.พ. 7")
async def get_kp7_forms(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """API สำหรับดึงรายการคำขอ ก.พ. 7 (ต้อง login)"""
    try:
        # แปลง status string เป็น enum
        status_filter = FormStatus(status) if status else None
        
        # ดึงข้อมูลจาก database
        forms = await get_form_submissions(
            db=db,
            form_type=FormType.KP7,
            status=status_filter,
            limit=limit,
            offset=offset
        )
        
        return {
            "forms": [
                {
                    "id": form.id,
                    "user_name": form.user_name,
                    "user_email": form.user_email,
                    "status": form.status,
                    "priority": form.priority,
                    "submitted_at": form.submitted_at.isoformat() if form.submitted_at else None,
                    "notes": form.notes
                }
                for form in forms
            ],
            "total": len(forms),
            "status": "success"
        }
    except Exception as e:
        return {
            "forms": [],
            "total": 0,
            "status": "error",
            "message": str(e)
        }

# === ID Card Forms Management ===
@router.get("/forms/id-card", response_class=HTMLResponse, summary="จัดการคำขอบัตรประจำตัว")
async def id_card_forms_page(request: Request):
    """หน้าจัดการคำขอบัตรประจำตัว"""
    return templates.TemplateResponse(
        "form_admin/id_card_forms.html",
        {"request": request, "title": "จัดการคำขอบัตรประจำตัว"}
    )

@router.get("/api/forms/id-card", summary="API รายการคำขอบัตรประจำตัว")
async def get_id_card_forms(
    status: Optional[str] = None,
    limit: int = 50, 
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """API สำหรับดึงรายการคำขอบัตรประจำตัว"""
    # TODO: Implement after database models
    return {
        "forms": [],
        "total": 0,
        "status": "placeholder"
    }

# === Reports & Analytics ===
@router.get("/reports", response_class=HTMLResponse, summary="รายงานและสถิติ")
async def reports_page(request: Request):
    """หน้ารายงานและสถิติ"""
    return templates.TemplateResponse(
        "form_admin/reports.html",
        {"request": request, "title": "รายงานและสถิติ"}
    )

@router.get("/analytics", response_class=HTMLResponse, summary="วิเคราะห์ข้อมูล")
async def analytics_page(request: Request):
    """หน้าวิเคราะห์ข้อมูล"""
    return templates.TemplateResponse(
        "form_admin/analytics.html",
        {"request": request, "title": "วิเคราะห์ข้อมูล"}
    )

# === User Management ===
@router.get("/users", response_class=HTMLResponse, summary="จัดการผู้ใช้งาน")
async def users_management_page(request: Request):
    """หน้าจัดการผู้ใช้งาน"""
    return templates.TemplateResponse(
        "form_admin/users.html",
        {"request": request, "title": "จัดการผู้ใช้งาน"}
    )

# === Settings ===
@router.get("/settings", response_class=HTMLResponse, summary="ตั้งค่าระบบ")
async def settings_page(request: Request):
    """หน้าตั้งค่าระบบ"""
    return templates.TemplateResponse(
        "form_admin/settings.html",
        {"request": request, "title": "ตั้งค่าระบบ"}
    )

# === API Health Check ===
@router.get("/health", summary="Forms Admin Health Check")
async def forms_admin_health():
    """Health check สำหรับ Forms Admin"""
    return {
        "status": "ok",
        "service": "Forms Admin",
        "version": "1.0.0",
        "endpoints": [
            "/form-admin/",
            "/form-admin/forms/kp7",
            "/form-admin/forms/id-card",
            "/form-admin/reports",
            "/form-admin/users"
        ]
    }
