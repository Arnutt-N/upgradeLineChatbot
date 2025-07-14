#!/usr/bin/env python3
"""
Quick script to check current friends status and send summary to Telegram
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc

sys.path.append('.')

from app.db.database import AsyncSessionLocal
from app.db.models import UserStatus, FriendActivity, TelegramNotification
from app.services.line_handler_enhanced import send_telegram_notification_enhanced
from app.utils.timezone import get_thai_time

async def get_friends_summary():
    """Get friends summary from database"""
    async with AsyncSessionLocal() as db:
        try:
            # Total users
            total_users_result = await db.execute(select(func.count(UserStatus.user_id)))
            total_users = total_users_result.scalar()
            
            # Active users (have recent activity)
            seven_days_ago = get_thai_time() - timedelta(days=7)
            recent_activity_result = await db.execute(
                select(func.count(UserStatus.user_id.distinct()))
                .where(UserStatus.last_activity_time > seven_days_ago)
            )
            active_users = recent_activity_result.scalar() or 0
            
            # New friends today
            today_start = get_thai_time().replace(hour=0, minute=0, second=0, microsecond=0)
            new_friends_today_result = await db.execute(
                select(func.count(FriendActivity.id))
                .where(FriendActivity.activity_type == 'follow')
                .where(FriendActivity.timestamp >= today_start)
            )
            new_friends_today = new_friends_today_result.scalar() or 0
            
            # Recent friends (last 24 hours)
            last_24h = get_thai_time() - timedelta(hours=24)
            recent_friends_result = await db.execute(
                select(FriendActivity.user_id, FriendActivity.user_profile, FriendActivity.timestamp)
                .where(FriendActivity.activity_type == 'follow')
                .where(FriendActivity.timestamp >= last_24h)
                .order_by(desc(FriendActivity.timestamp))
                .limit(10)
            )
            recent_friends = recent_friends_result.fetchall()
            
            # Recent unfollows (last 24 hours)
            recent_unfollows_result = await db.execute(
                select(FriendActivity.user_id, FriendActivity.timestamp)
                .where(FriendActivity.activity_type == 'unfollow')
                .where(FriendActivity.timestamp >= last_24h)
                .order_by(desc(FriendActivity.timestamp))
                .limit(5)
            )
            recent_unfollows = recent_unfollows_result.fetchall()
            
            # Telegram notifications status
            telegram_status_result = await db.execute(
                select(TelegramNotification.status, func.count(TelegramNotification.id))
                .where(TelegramNotification.created_at >= last_24h)
                .group_by(TelegramNotification.status)
            )
            telegram_status = dict(telegram_status_result.fetchall())
            
            return {
                "total_users": total_users,
                "active_users": active_users,
                "new_friends_today": new_friends_today,
                "recent_friends": recent_friends,
                "recent_unfollows": recent_unfollows,
                "telegram_status": telegram_status
            }
            
        except Exception as e:
            print(f"❌ Error getting friends summary: {e}")
            return None

async def send_friends_status_report():
    """Send friends status report to Telegram"""
    summary = await get_friends_summary()
    if not summary:
        return False
    
    thai_time = get_thai_time()
    
    # Create report message
    report = f"""📊 รายงานสถานะเพื่อน - {thai_time.strftime('%Y-%m-%d %H:%M')}

👥 ผู้ใช้ทั้งหมด: {summary['total_users']:,}
✅ ผู้ใช้ที่มีกิจกรรม (7 วันล่าสุด): {summary['active_users']:,}
🆕 เพื่อนใหม่วันนี้: {summary['new_friends_today']:,}

📈 กิจกรรมล่าสุด (24 ชม.):"""
    
    # Add recent friends
    if summary['recent_friends']:
        report += "\n\n🆕 เพื่อนใหม่:"
        for user_id, profile_json, timestamp in summary['recent_friends']:
            try:
                import json
                profile = json.loads(profile_json) if profile_json else {}
                name = profile.get('display_name', f'User {user_id[-6:]}')
                time_str = timestamp.strftime('%H:%M')
                report += f"\n- {name} ({time_str})"
            except:
                report += f"\n- {user_id[-6:]} ({timestamp.strftime('%H:%M')})"
        
        if len(summary['recent_friends']) >= 10:
            report += "\n... (แสดงแค่ 10 คนแรก)"
    
    # Add recent unfollows
    if summary['recent_unfollows']:
        report += "\n\n👋 ยกเลิกติดตาม:"
        for user_id, timestamp in summary['recent_unfollows']:
            time_str = timestamp.strftime('%H:%M')
            report += f"\n- {user_id[-6:]} ({time_str})"
    
    # Add Telegram notification status
    if summary['telegram_status']:
        report += "\n\n📱 สถานะแจ้งเตือน Telegram:"
        for status, count in summary['telegram_status'].items():
            status_emoji = {"sent": "✅", "failed": "❌", "pending": "⏳"}.get(status, "📍")
            report += f"\n{status_emoji} {status}: {count}"
    
    # Send report
    async with AsyncSessionLocal() as db:
        try:
            await send_telegram_notification_enhanced(
                db=db,
                notification_type="friends_status_report",
                title="📊 รายงานสถานะเพื่อน",
                message=report,
                priority=1,
                data=summary
            )
            print("✅ Friends status report sent to Telegram")
            return True
        except Exception as e:
            print(f"❌ Error sending report: {e}")
            return False

async def main():
    """Main entry point"""
    print("📊 Generating friends status report...")
    success = await send_friends_status_report()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)