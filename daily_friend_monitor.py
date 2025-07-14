#!/usr/bin/env python3
"""
Daily friend monitoring script - lighter version for regular automated checks
This script runs daily to:
1. Send daily friends summary
2. Check for any missed friend activities
3. Monitor friend growth trends
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_

sys.path.append('.')

from app.db.database import AsyncSessionLocal
from app.db.models import UserStatus, FriendActivity, TelegramNotification
from app.services.line_handler_enhanced import send_telegram_notification_enhanced
from app.db.crud_enhanced import log_system_event
from app.utils.timezone import get_thai_time

class DailyFriendMonitor:
    def __init__(self):
        self.stats = {}
    
    async def get_daily_stats(self, db):
        """Get daily friend statistics"""
        thai_time = get_thai_time()
        today_start = thai_time.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_ago = today_start - timedelta(days=7)
        
        # Today's new friends
        today_friends_result = await db.execute(
            select(func.count(FriendActivity.id))
            .where(FriendActivity.activity_type == 'follow')
            .where(FriendActivity.timestamp >= today_start)
        )
        today_friends = today_friends_result.scalar() or 0
        
        # Yesterday's new friends
        yesterday_friends_result = await db.execute(
            select(func.count(FriendActivity.id))
            .where(FriendActivity.activity_type == 'follow')
            .where(and_(
                FriendActivity.timestamp >= yesterday_start,
                FriendActivity.timestamp < today_start
            ))
        )
        yesterday_friends = yesterday_friends_result.scalar() or 0
        
        # This week's new friends
        week_friends_result = await db.execute(
            select(func.count(FriendActivity.id))
            .where(FriendActivity.activity_type == 'follow')
            .where(FriendActivity.timestamp >= week_ago)
        )
        week_friends = week_friends_result.scalar() or 0
        
        # Total current friends
        total_friends_result = await db.execute(
            select(func.count(UserStatus.user_id))
        )
        total_friends = total_friends_result.scalar() or 0
        
        # Today's unfollows
        today_unfollows_result = await db.execute(
            select(func.count(FriendActivity.id))
            .where(FriendActivity.activity_type == 'unfollow')
            .where(FriendActivity.timestamp >= today_start)
        )
        today_unfollows = today_unfollows_result.scalar() or 0
        
        # Net growth today
        net_growth = today_friends - today_unfollows
        
        # Growth trend
        growth_trend = "📈" if today_friends > yesterday_friends else "📉" if today_friends < yesterday_friends else "➡️"
        
        return {
            "today_friends": today_friends,
            "yesterday_friends": yesterday_friends,
            "week_friends": week_friends,
            "total_friends": total_friends,
            "today_unfollows": today_unfollows,
            "net_growth": net_growth,
            "growth_trend": growth_trend
        }
    
    async def get_recent_activities(self, db):
        """Get recent friend activities for the report"""
        thai_time = get_thai_time()
        last_24h = thai_time - timedelta(hours=24)
        
        # Recent new friends
        recent_friends_result = await db.execute(
            select(FriendActivity.user_id, FriendActivity.user_profile, FriendActivity.timestamp)
            .where(FriendActivity.activity_type == 'follow')
            .where(FriendActivity.timestamp >= last_24h)
            .order_by(desc(FriendActivity.timestamp))
            .limit(5)
        )
        recent_friends = recent_friends_result.fetchall()
        
        return {"recent_friends": recent_friends}
    
    async def generate_daily_report(self, db):
        """Generate daily friend monitoring report"""
        thai_time = get_thai_time()
        stats = await self.get_daily_stats(db)
        activities = await self.get_recent_activities(db)
        
        # Calculate growth percentage
        growth_pct = 0
        if stats["yesterday_friends"] > 0:
            growth_pct = ((stats["today_friends"] - stats["yesterday_friends"]) / stats["yesterday_friends"]) * 100
        
        # Create report
        report = f"""📊 รายงานเพื่อนประจำวัน
🗓️ {thai_time.strftime('%Y-%m-%d')} ({thai_time.strftime('%A')})

📈 สถิติวันนี้:
🆕 เพื่อนใหม่: {stats['today_friends']}
👋 ยกเลิกติดตาม: {stats['today_unfollows']}
📊 เติบโตสุทธิ: {stats['net_growth']:+d}
👥 เพื่อนทั้งหมด: {stats['total_friends']:,}

📉 เปรียบเทียบ:
🔸 เมื่อวาน: {stats['yesterday_friends']} ({growth_pct:+.1f}%) {stats['growth_trend']}
🔸 สัปดาห์นี้: {stats['week_friends']} คน"""
        
        # Add recent friends if any
        if activities["recent_friends"]:
            report += "\n\n🆕 เพื่อนใหม่ล่าสุด:"
            for user_id, profile_json, timestamp in activities["recent_friends"]:
                try:
                    import json
                    profile = json.loads(profile_json) if profile_json else {}
                    name = profile.get('display_name', f'User {user_id[-6:]}')
                    time_str = timestamp.strftime('%H:%M')
                    report += f"\n• {name} ({time_str})"
                except:
                    report += f"\n• {user_id[-6:]} ({timestamp.strftime('%H:%M')})"
        
        # Add insights
        if stats["today_friends"] == 0:
            report += "\n\n💡 ไม่มีเพื่อนใหม่วันนี้"
        elif stats["today_friends"] > stats["yesterday_friends"]:
            report += f"\n\n🎉 เติบโตดีกว่าเมื่อวาน {stats['today_friends'] - stats['yesterday_friends']} คน!"
        elif stats["net_growth"] < 0:
            report += f"\n\n⚠️ จำนวนเพื่อนลดลง {abs(stats['net_growth'])} คน"
        
        self.stats = stats
        return report
    
    async def send_daily_report(self):
        """Send daily report to Telegram"""
        async with AsyncSessionLocal() as db:
            try:
                report = await self.generate_daily_report(db)
                
                await send_telegram_notification_enhanced(
                    db=db,
                    notification_type="daily_friends_report",
                    title="📊 รายงานเพื่อนประจำวัน",
                    message=report,
                    priority=2,
                    data=self.stats
                )
                
                await log_system_event(
                    db=db,
                    level="info",
                    category="friend_management",
                    subcategory="daily_report_sent",
                    message="Daily friends report sent successfully",
                    details=self.stats
                )
                
                print("✅ Daily friends report sent to Telegram")
                return True
                
            except Exception as e:
                print(f"❌ Error sending daily report: {e}")
                await log_system_event(
                    db=db,
                    level="error",
                    category="friend_management", 
                    subcategory="daily_report_failed",
                    message=f"Failed to send daily report: {str(e)}",
                    details={"error": str(e)}
                )
                return False
    
    async def check_notification_health(self):
        """Check if Telegram notifications are working properly"""
        async with AsyncSessionLocal() as db:
            try:
                # Check recent notification failures
                last_24h = get_thai_time() - timedelta(hours=24)
                failed_notifications_result = await db.execute(
                    select(func.count(TelegramNotification.id))
                    .where(TelegramNotification.status == 'failed')
                    .where(TelegramNotification.created_at >= last_24h)
                )
                failed_count = failed_notifications_result.scalar() or 0
                
                if failed_count > 5:
                    await send_telegram_notification_enhanced(
                        db=db,
                        notification_type="system_alert",
                        title="⚠️ แจ้งเตือนระบบ",
                        message=f"มีการแจ้งเตือนล้มเหลว {failed_count} ครั้งใน 24 ชม.ล่าสุด\nกรุณาตรวจสอบการตั้งค่า Telegram",
                        priority=3,
                        data={"failed_count": failed_count, "period": "24h"}
                    )
                    print(f"⚠️ High notification failure rate detected: {failed_count}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error checking notification health: {e}")
                return False

async def main():
    """Main entry point"""
    print("📊 Starting daily friend monitoring...")
    
    monitor = DailyFriendMonitor()
    
    # Send daily report
    success = await monitor.send_daily_report()
    if not success:
        return 1
    
    # Check notification health
    await monitor.check_notification_health()
    
    print("✅ Daily friend monitoring completed")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)