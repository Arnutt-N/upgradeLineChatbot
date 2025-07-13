# Enhanced API Endpoints for History and Analytics
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.services.history_service import history_service
from app.services.telegram_service import telegram_service
from app.db.crud_enhanced import (
    get_chat_history, get_friend_activities, get_telegram_statistics,
    get_system_logs, log_system_event
)

router = APIRouter(prefix="/api/enhanced", tags=["Enhanced Analytics"])

# ========================================
# Chat Analytics Endpoints
# ========================================

@router.get("/chat/overview")
async def get_chat_overview(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """ภาพรวมการแชท"""
    try:
        overview = await history_service.get_chat_overview(db, days)
        return {"success": True, "data": overview}
    except Exception as e:
        await log_system_event(
            db=db,
            level="error",
            category="api",
            subcategory="chat_overview_error",
            message=f"Error getting chat overview: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/timeline")
async def get_chat_timeline(
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """Timeline การแชทรายวัน"""
    try:
        timeline = await history_service.get_chat_timeline(db, days)
        return {"success": True, "data": timeline}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/user/{user_id}")
async def get_user_chat_history(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """ประวัติการแชทของผู้ใช้"""
    try:
        history = await history_service.get_user_chat_history(db, user_id, limit, offset)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/export")
async def export_chat_history(
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Export ประวัติการแชทเป็น CSV"""
    try:
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        csv_data = await history_service.export_chat_history_csv(
            db, user_id, start_dt, end_dt
        )
        
        from fastapi.responses import Response
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=chat_history.csv"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# Friend Analytics Endpoints
# ========================================

@router.get("/friends/analytics")
async def get_friend_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """วิเคราะห์ข้อมูลเพื่อน"""
    try:
        analytics = await history_service.get_friend_analytics(db, days)
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/friends/recent")
async def get_recent_friend_activities(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """กิจกรรมเพื่อนล่าสุด"""
    try:
        activities = await history_service.get_recent_friend_activities(db, limit)
        return {"success": True, "data": activities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# Telegram Analytics Endpoints
# ========================================

@router.get("/telegram/analytics")
async def get_telegram_analytics(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    """วิเคราะห์การแจ้งเตือน Telegram"""
    try:
        analytics = await history_service.get_telegram_analytics(db, days)
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telegram/test")
async def test_telegram_connection(db: AsyncSession = Depends(get_db)):
    """ทดสอบการเชื่อมต่อ Telegram"""
    try:
        result = await telegram_service.test_connection(db)
        return {"success": result["success"], "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/telegram/process-queue")
async def process_telegram_queue(db: AsyncSession = Depends(get_db)):
    """ประมวลผล queue การแจ้งเตือน Telegram แบบ manual"""
    try:
        stats = await telegram_service.process_notification_queue(db)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# System Health Endpoints
# ========================================

@router.get("/system/health")
async def get_system_health(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """สุขภาพระบบ"""
    try:
        health = await history_service.get_system_health(db, hours)
        return {"success": True, "data": health}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/logs")
async def get_system_logs_api(
    level: Optional[str] = Query(None, regex="^(debug|info|warning|error|critical)$"),
    category: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """ดึง System Logs"""
    try:
        logs = await get_system_logs(db, level, category, None, limit, offset)
        
        formatted_logs = []
        for log in logs:
            details = {}
            if log.details:
                try:
                    import json
                    details = json.loads(log.details)
                except:
                    pass
            
            formatted_logs.append({
                "id": log.id,
                "log_level": log.log_level,
                "category": log.category,
                "subcategory": log.subcategory,
                "message": log.message,
                "details": details,
                "user_id": log.user_id,
                "timestamp": log.timestamp.isoformat()
            })
        
        return {"success": True, "data": formatted_logs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# Dashboard Summary Endpoint
# ========================================

@router.get("/dashboard/summary")
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)):
    """สรุปข้อมูลสำหรับ Dashboard"""
    try:
        # รวบรวมข้อมูลจากหลายแหล่ง
        chat_overview = await history_service.get_chat_overview(db, 7)  # 7 วันล่าสุด
        friend_analytics = await history_service.get_friend_analytics(db, 7)
        telegram_analytics = await history_service.get_telegram_analytics(db, 7)
        system_health = await history_service.get_system_health(db, 24)  # 24 ชั่วโมงล่าสุด
        
        summary = {
            "chat": {
                "total_messages_7d": chat_overview["total_messages"],
                "active_users_7d": chat_overview["active_users"],
                "avg_messages_per_user": chat_overview["avg_messages_per_user"]
            },
            "friends": {
                "new_followers_7d": friend_analytics["activities_summary"].get("follow", 0),
                "unfollowers_7d": friend_analytics["activities_summary"].get("unfollow", 0),
                "net_growth_7d": friend_analytics["net_followers"]
            },
            "telegram": {
                "notifications_sent_7d": telegram_analytics["notifications_by_status"].get("sent", 0),
                "success_rate": telegram_analytics["success_rate"],
                "total_notifications_7d": telegram_analytics["total_notifications"]
            },
            "system": {
                "error_rate_24h": system_health["error_rate"],
                "total_logs_24h": system_health["total_logs"],
                "avg_response_time": system_health["performance"]["avg_response_time_ms"]
            }
        }
        
        return {"success": True, "data": summary}
        
    except Exception as e:
        await log_system_event(
            db=db,
            level="error",
            category="api",
            subcategory="dashboard_summary_error",
            message=f"Error getting dashboard summary: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=str(e))

# Export router
__all__ = ["router"]
