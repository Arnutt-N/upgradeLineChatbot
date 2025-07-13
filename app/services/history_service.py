# History Service - Analytics and Reporting
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc

from app.db.models import ChatHistory, FriendActivity, TelegramNotification, SystemLogs, UserStatus
from app.db.crud_enhanced import log_system_event

class HistoryService:
    """Service สำหรับการจัดการประวัติและการวิเคราะห์ข้อมูล"""
    
    def __init__(self):
        pass
    
    # ========================================
    # Chat Analytics
    # ========================================
    
    async def get_chat_overview(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """ภาพรวมการแชท"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Total messages
        total_query = select(func.count(ChatHistory.id)).where(
            ChatHistory.timestamp >= start_date
        )
        total_result = await db.execute(total_query)
        total_messages = total_result.scalar() or 0
        
        # Messages by type
        type_query = select(
            ChatHistory.message_type,
            func.count(ChatHistory.id)
        ).where(
            ChatHistory.timestamp >= start_date
        ).group_by(ChatHistory.message_type)
        
        type_result = await db.execute(type_query)
        messages_by_type = dict(type_result.fetchall())
        
        # Active users
        users_query = select(func.count(func.distinct(ChatHistory.user_id))).where(
            ChatHistory.timestamp >= start_date
        )
        users_result = await db.execute(users_query)
        active_users = users_result.scalar() or 0
        
        # Sessions
        sessions_query = select(func.count(func.distinct(ChatHistory.session_id))).where(
            ChatHistory.timestamp >= start_date
        )
        sessions_result = await db.execute(sessions_query)
        total_sessions = sessions_result.scalar() or 0
        
        return {
            "period_days": days,
            "total_messages": total_messages,
            "messages_by_type": messages_by_type,
            "active_users": active_users,
            "total_sessions": total_sessions,
            "avg_messages_per_user": round(total_messages / active_users, 2) if active_users > 0 else 0
        }
    
    async def get_chat_timeline(self, db: AsyncSession, days: int = 7) -> List[Dict[str, Any]]:
        """Timeline การแชทรายวัน"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Messages per day
        daily_query = select(
            func.date(ChatHistory.timestamp).label('date'),
            ChatHistory.message_type,
            func.count(ChatHistory.id).label('count')
        ).where(
            ChatHistory.timestamp >= start_date
        ).group_by(
            func.date(ChatHistory.timestamp),
            ChatHistory.message_type
        ).order_by('date')
        
        daily_result = await db.execute(daily_query)
        daily_data = daily_result.fetchall()
        
        # จัดรูปแบบข้อมูล
        timeline = {}
        for date, msg_type, count in daily_data:
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in timeline:
                timeline[date_str] = {"date": date_str, "user": 0, "bot": 0, "admin": 0}
            timeline[date_str][msg_type] = count
        
        return list(timeline.values())
    
    async def get_user_chat_history(
        self, 
        db: AsyncSession, 
        user_id: str, 
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """ประวัติการแชทของผู้ใช้คนใดคนหนึ่ง"""
        
        # Get messages
        messages_query = select(ChatHistory).where(
            ChatHistory.user_id == user_id
        ).order_by(ChatHistory.timestamp.desc()).limit(limit).offset(offset)
        
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Get user info
        user_query = select(UserStatus).where(UserStatus.user_id == user_id)
        user_result = await db.execute(user_query)
        user_info = user_result.scalar_one_or_none()
        
        # Count total messages
        count_query = select(func.count(ChatHistory.id)).where(
            ChatHistory.user_id == user_id
        )
        count_result = await db.execute(count_query)
        total_messages = count_result.scalar() or 0
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            extra_data = {}
            if msg.extra_data:
                try:
                    import json
                    extra_data = json.loads(msg.extra_data)
                except:
                    pass
            
            formatted_messages.append({
                "id": msg.id,
                "message_type": msg.message_type,
                "message_content": msg.message_content,
                "timestamp": msg.timestamp.isoformat(),
                "admin_user_id": msg.admin_user_id,
                "is_read": msg.is_read,
                "session_id": msg.session_id,
                "extra_data": extra_data
            })
        
        return {
            "user_id": user_id,
            "user_info": {
                "display_name": user_info.display_name if user_info else "ไม่ระบุ",
                "picture_url": user_info.picture_url if user_info else None,
                "is_in_live_chat": user_info.is_in_live_chat if user_info else False,
                "chat_mode": user_info.chat_mode if user_info else "manual"
            },
            "total_messages": total_messages,
            "messages": formatted_messages
        }
    
    # ========================================
    # Friend Analytics
    # ========================================
    
    async def get_friend_analytics(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """วิเคราะห์ข้อมูลเพื่อน"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Activities by type
        activity_query = select(
            FriendActivity.activity_type,
            func.count(FriendActivity.id)
        ).where(
            FriendActivity.timestamp >= start_date
        ).group_by(FriendActivity.activity_type)
        
        activity_result = await db.execute(activity_query)
        activities = dict(activity_result.fetchall())
        
        # Daily activity
        daily_query = select(
            func.date(FriendActivity.timestamp).label('date'),
            FriendActivity.activity_type,
            func.count(FriendActivity.id).label('count')
        ).where(
            FriendActivity.timestamp >= start_date
        ).group_by(
            func.date(FriendActivity.timestamp),
            FriendActivity.activity_type
        ).order_by('date')
        
        daily_result = await db.execute(daily_query)
        daily_activities = daily_result.fetchall()
        
        # Format daily data
        daily_timeline = {}
        for date, activity_type, count in daily_activities:
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in daily_timeline:
                daily_timeline[date_str] = {"date": date_str, "follow": 0, "unfollow": 0, "block": 0, "unblock": 0}
            daily_timeline[date_str][activity_type] = count
        
        return {
            "period_days": days,
            "activities_summary": activities,
            "daily_timeline": list(daily_timeline.values()),
            "net_followers": activities.get('follow', 0) - activities.get('unfollow', 0)
        }
    
    async def get_recent_friend_activities(
        self, 
        db: AsyncSession, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """กิจกรรมเพื่อนล่าสุด"""
        
        query = select(FriendActivity).order_by(
            FriendActivity.timestamp.desc()
        ).limit(limit)
        
        result = await db.execute(query)
        activities = result.scalars().all()
        
        formatted_activities = []
        for activity in activities:
            user_profile = {}
            if activity.user_profile:
                try:
                    import json
                    user_profile = json.loads(activity.user_profile)
                except:
                    pass
            
            formatted_activities.append({
                "id": activity.id,
                "user_id": activity.user_id,
                "activity_type": activity.activity_type,
                "user_profile": user_profile,
                "timestamp": activity.timestamp.isoformat(),
                "source": activity.source
            })
        
        return formatted_activities
    
    # ========================================
    # Telegram Analytics
    # ========================================
    
    async def get_telegram_analytics(self, db: AsyncSession, days: int = 30) -> Dict[str, Any]:
        """วิเคราะห์การแจ้งเตือน Telegram"""
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Notifications by status
        status_query = select(
            TelegramNotification.status,
            func.count(TelegramNotification.id)
        ).where(
            TelegramNotification.timestamp >= start_date
        ).group_by(TelegramNotification.status)
        
        status_result = await db.execute(status_query)
        notifications_by_status = dict(status_result.fetchall())
        
        # Notifications by type
        type_query = select(
            TelegramNotification.notification_type,
            func.count(TelegramNotification.id)
        ).where(
            TelegramNotification.timestamp >= start_date
        ).group_by(TelegramNotification.notification_type)
        
        type_result = await db.execute(type_query)
        notifications_by_type = dict(type_result.fetchall())
        
        # Success rate
        total_notifications = sum(notifications_by_status.values())
        sent_notifications = notifications_by_status.get('sent', 0)
        success_rate = (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0
        
        # Failed notifications
        failed_query = select(TelegramNotification).where(
            and_(
                TelegramNotification.status == 'failed',
                TelegramNotification.timestamp >= start_date
            )
        ).order_by(TelegramNotification.timestamp.desc()).limit(10)
        
        failed_result = await db.execute(failed_query)
        recent_failures = failed_result.scalars().all()
        
        return {
            "period_days": days,
            "notifications_by_status": notifications_by_status,
            "notifications_by_type": notifications_by_type,
            "total_notifications": total_notifications,
            "success_rate": round(success_rate, 2),
            "recent_failures": [
                {
                    "id": f.id,
                    "notification_type": f.notification_type,
                    "error_message": f.error_message,
                    "timestamp": f.timestamp.isoformat()
                }
                for f in recent_failures
            ]
        }
    
    # ========================================
    # System Analytics
    # ========================================
    
    async def get_system_health(self, db: AsyncSession, hours: int = 24) -> Dict[str, Any]:
        """สุขภาพระบบ"""
        
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Logs by level
        level_query = select(
            SystemLogs.log_level,
            func.count(SystemLogs.id)
        ).where(
            SystemLogs.timestamp >= start_time
        ).group_by(SystemLogs.log_level)
        
        level_result = await db.execute(level_query)
        logs_by_level = dict(level_result.fetchall())
        
        # Logs by category
        category_query = select(
            SystemLogs.category,
            func.count(SystemLogs.id)
        ).where(
            SystemLogs.timestamp >= start_time
        ).group_by(SystemLogs.category)
        
        category_result = await db.execute(category_query)
        logs_by_category = dict(category_result.fetchall())
        
        # Recent errors
        error_query = select(SystemLogs).where(
            and_(
                SystemLogs.log_level == 'error',
                SystemLogs.timestamp >= start_time
            )
        ).order_by(SystemLogs.timestamp.desc()).limit(10)
        
        error_result = await db.execute(error_query)
        recent_errors = error_result.scalars().all()
        
        # Performance metrics
        perf_query = select(
            func.avg(SystemLogs.performance_ms),
            func.max(SystemLogs.performance_ms),
            func.count(SystemLogs.id)
        ).where(
            and_(
                SystemLogs.performance_ms.isnot(None),
                SystemLogs.timestamp >= start_time
            )
        )
        
        perf_result = await db.execute(perf_query)
        avg_perf, max_perf, perf_count = perf_result.fetchone() or (0, 0, 0)
        
        return {
            "period_hours": hours,
            "logs_by_level": logs_by_level,
            "logs_by_category": logs_by_category,
            "total_logs": sum(logs_by_level.values()),
            "error_rate": round((logs_by_level.get('error', 0) / sum(logs_by_level.values()) * 100), 2) if sum(logs_by_level.values()) > 0 else 0,
            "performance": {
                "avg_response_time_ms": round(avg_perf or 0, 2),
                "max_response_time_ms": max_perf or 0,
                "measured_requests": perf_count
            },
            "recent_errors": [
                {
                    "id": e.id,
                    "category": e.category,
                    "message": e.message,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in recent_errors
            ]
        }
    
    # ========================================
    # Export Functions
    # ========================================
    
    async def export_chat_history_csv(
        self, 
        db: AsyncSession, 
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> str:
        """Export chat history เป็น CSV"""
        
        import csv
        import io
        
        query = select(ChatHistory)
        
        if user_id:
            query = query.where(ChatHistory.user_id == user_id)
        if start_date:
            query = query.where(ChatHistory.timestamp >= start_date)
        if end_date:
            query = query.where(ChatHistory.timestamp <= end_date)
        
        query = query.order_by(ChatHistory.timestamp)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'ID', 'User ID', 'Message Type', 'Message Content', 
            'Admin User ID', 'Is Read', 'Session ID', 'Timestamp'
        ])
        
        # Data
        for msg in messages:
            writer.writerow([
                msg.id, msg.user_id, msg.message_type, msg.message_content,
                msg.admin_user_id, msg.is_read, msg.session_id, 
                msg.timestamp.isoformat()
            ])
        
        return output.getvalue()

# ========================================
# Global Instance
# ========================================

history_service = HistoryService()

# Export
__all__ = ['HistoryService', 'history_service']
