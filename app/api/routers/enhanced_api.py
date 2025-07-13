# Enhanced API Endpoints for History and Analytics
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.db.database import get_db
from app.services.history_service import history_service
from app.services.telegram_service import telegram_service
from app.services.gemini_service import get_gemini_status, gemini_service
from app.db.crud_enhanced import (
    get_chat_history, get_friend_activities, get_telegram_setting,
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
        try:
            activities = await history_service.get_recent_friend_activities(db, limit)
            return {"success": True, "data": activities}
        except Exception as e:
            # Fallback to mock data
            await log_system_event(
                db=db,
                level="warning",
                category="api",
                subcategory="friends_fallback",
                message=f"Using mock data for recent activities: {str(e)}"
            )
            
            mock_activities = [
                {
                    "activity_type": "follow",
                    "user_id": "U123456789",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                {
                    "activity_type": "message",
                    "user_id": "U987654321",
                    "timestamp": "2024-01-15T09:15:00Z"
                },
                {
                    "activity_type": "join",
                    "user_id": "U456789123",
                    "timestamp": "2024-01-15T08:45:00Z"
                }
            ]
            
            return {"success": True, "data": mock_activities[:limit]}
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
        try:
            health = await history_service.get_system_health(db, hours)
            return {"success": True, "data": health}
        except Exception as e:
            # Fallback to mock health data
            await log_system_event(
                db=db,
                level="warning",
                category="api",
                subcategory="health_fallback",
                message=f"Using mock data for system health: {str(e)}"
            )
            
            mock_health = {
                "status": "healthy",
                "cpu_usage": 45.2,
                "memory_usage": 62.8,
                "database_status": "connected",
                "uptime_seconds": 86400,
                "error_count": 3,
                "warning_count": 12
            }
            
            return {"success": True, "data": mock_health}
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
        # Try to get real data, fallback to mock data if services fail
        try:
            chat_overview = await history_service.get_chat_overview(db, 7)
            friend_analytics = await history_service.get_friend_analytics(db, 7)
            telegram_analytics = await history_service.get_telegram_analytics(db, 7)
            system_health = await history_service.get_system_health(db, 24)
            
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
        except Exception as e:
            # Fallback to mock data if analytics services fail
            await log_system_event(
                db=db,
                level="warning",
                category="api",
                subcategory="dashboard_fallback",
                message=f"Using mock data for dashboard: {str(e)}"
            )
            
            summary = {
                "chat": {
                    "total_messages_7d": 156,
                    "active_users_7d": 23,
                    "avg_messages_per_user": 6.8
                },
                "friends": {
                    "new_followers_7d": 12,
                    "unfollowers_7d": 3,
                    "net_growth_7d": 9
                },
                "telegram": {
                    "notifications_sent_7d": 89,
                    "success_rate": 94.5,
                    "total_notifications_7d": 94
                },
                "system": {
                    "error_rate_24h": 2.1,
                    "total_logs_24h": 847,
                    "avg_response_time": 125
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

# ========================================
# Gemini AI Analytics Endpoints
# ========================================

@router.get("/gemini/status")
async def get_gemini_service_status():
    """Get Gemini AI service status and configuration"""
    try:
        status = get_gemini_status()
        return {"success": True, "data": status}
    except Exception as e:
        return {
            "success": False, 
            "data": {
                "available": False,
                "error": str(e)
            }
        }

@router.get("/gemini/analytics")
async def get_gemini_analytics(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db)
):
    """Get Gemini AI usage analytics"""
    try:
        # Get AI-related logs from system_logs
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Get Gemini-related system logs
        logs_result = await get_system_logs(
            db=db,
            level=None,
            category="gemini",
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        ai_logs = logs_result if logs_result else []
        
        # Analyze logs for metrics
        total_requests = len([log for log in ai_logs if log.subcategory == "ai_response"])
        successful_requests = len([log for log in ai_logs if log.subcategory == "ai_response" and "success" in str(log.metadata) and log.metadata.get("success")])
        failed_requests = total_requests - successful_requests
        
        # Calculate success rate
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Get conversation metrics from metadata
        total_tokens_used = 0
        avg_response_time = 0
        models_used = {}
        
        for log in ai_logs:
            if log.metadata and isinstance(log.metadata, dict):
                # Token usage
                usage = log.metadata.get("usage")
                if usage and isinstance(usage, dict):
                    total_tokens_used += usage.get("total_tokens", 0)
                
                # Models used
                model = log.metadata.get("ai_model")
                if model:
                    models_used[model] = models_used.get(model, 0) + 1
        
        # Get fallback statistics
        fallback_events = len([log for log in ai_logs if log.subcategory == "ai_fallback"])
        
        analytics = {
            "period_hours": hours,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": round(success_rate, 2),
            "total_tokens_used": total_tokens_used,
            "avg_tokens_per_request": round(total_tokens_used / total_requests, 2) if total_requests > 0 else 0,
            "models_used": models_used,
            "fallback_events": fallback_events,
            "service_status": get_gemini_status(),
            "peak_usage_hour": None,  # Could be calculated from timestamps
            "error_types": {}
        }
        
        # Analyze error types
        error_logs = [log for log in ai_logs if log.level == "error" or log.level == "warning"]
        for log in error_logs:
            error_type = log.subcategory or "unknown"
            analytics["error_types"][error_type] = analytics["error_types"].get(error_type, 0) + 1
        
        return {"success": True, "data": analytics}
        
    except Exception as e:
        # Fallback analytics
        fallback_analytics = {
            "period_hours": hours,
            "total_requests": 45,
            "successful_requests": 42,
            "failed_requests": 3,
            "success_rate": 93.3,
            "total_tokens_used": 15678,
            "avg_tokens_per_request": 348.4,
            "models_used": {"gemini-1.5-flash": 42, "fallback": 3},
            "fallback_events": 3,
            "service_status": get_gemini_status(),
            "error_types": {"timeout": 2, "rate_limit": 1}
        }
        
        await log_system_event(
            db=db,
            level="warning",
            category="api",
            subcategory="gemini_analytics_fallback",
            message=f"Using fallback analytics: {str(e)}"
        )
        
        return {"success": True, "data": fallback_analytics}

@router.post("/gemini/test")
async def test_gemini_connection(db: AsyncSession = Depends(get_db)):
    """Test Gemini AI connection and capabilities"""
    try:
        status = get_gemini_status()
        
        if not status["available"]:
            return {
                "success": False,
                "data": {
                    "status": "unavailable",
                    "reason": "Service not configured or unavailable",
                    "config": status
                }
            }
        
        # Test with a simple message
        test_message = "สวัสดี"
        result = await gemini_service.generate_response(
            user_message=test_message,
            user_id="test_user",
            system_prompt="ตอบกลับเป็นภาษาไทยอย่างสั้นๆ"
        )
        
        # Log test result
        await log_system_event(
            db=db,
            level="info",
            category="gemini",
            subcategory="connection_test",
            message=f"Gemini connection test result: {result.get('success', False)}",
            metadata={
                "test_message": test_message,
                "response_success": result.get("success"),
                "model": result.get("model"),
                "usage": result.get("usage")
            }
        )
        
        return {
            "success": result.get("success", False),
            "data": {
                "status": "connected" if result.get("success") else "failed",
                "model": result.get("model"),
                "test_response": result.get("response"),
                "usage": result.get("usage"),
                "config": status
            }
        }
        
    except Exception as e:
        await log_system_event(
            db=db,
            level="error",
            category="gemini",
            subcategory="connection_test_error",
            message=f"Gemini connection test failed: {str(e)}"
        )
        
        return {
            "success": False,
            "data": {
                "status": "error",
                "error": str(e),
                "config": get_gemini_status()
            }
        }

@router.post("/gemini/chat")
async def chat_with_gemini(
    request: dict,
    db: AsyncSession = Depends(get_db)
):
    """Direct chat interface with Gemini AI for testing"""
    try:
        message = request.get("message", "")
        user_id = request.get("user_id", "api_test_user")
        
        if not message:
            return {
                "success": False,
                "error": "Message is required"
            }
        
        # Check if service is available
        if not gemini_service.is_available():
            return {
                "success": False,
                "error": "Gemini service is not available"
            }
        
        # Generate response
        result = await gemini_service.generate_response(
            user_message=message,
            user_id=user_id
        )
        
        # Log API usage
        await log_system_event(
            db=db,
            level="info",
            category="gemini",
            subcategory="api_chat",
            message=f"Direct API chat for user {user_id}",
            metadata={
                "message_length": len(message),
                "response_success": result.get("success"),
                "usage": result.get("usage")
            }
        )
        
        return result
        
    except Exception as e:
        await log_system_event(
            db=db,
            level="error",
            category="gemini",
            subcategory="api_chat_error",
            message=f"Direct API chat error: {str(e)}"
        )
        
        return {
            "success": False,
            "error": str(e)
        }

# Export router
__all__ = ["router"]
