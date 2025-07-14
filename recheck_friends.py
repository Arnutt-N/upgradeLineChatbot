#!/usr/bin/env python3
"""
Script to recheck all user friends lists and notify Telegram of new friends
This script will:
1. Get all current users from database
2. Sync with current friends from LINE Bot API
3. Detect new friends and notify via Telegram
4. Update friend activity records
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import List, Dict, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

# Add the project root to the path
sys.path.append('.')

from app.core.config import settings
from app.db.database import get_db, AsyncSessionLocal
from app.db.models import UserStatus, FriendActivity
from app.db.crud_enhanced import save_friend_activity, log_system_event
from app.services.line_handler_enhanced import (
    get_user_profile_enhanced, 
    send_telegram_notification_enhanced
)
from app.utils.timezone import get_thai_time
from linebot.v3.messaging import AsyncApiClient, AsyncMessagingApi, Configuration
import httpx

class FriendListChecker:
    def __init__(self):
        self.line_bot_api = None
        self.total_users = 0
        self.new_friends = 0
        self.updated_profiles = 0
        self.errors = 0
        
    async def initialize_line_api(self):
        """Initialize LINE Bot API"""
        try:
            if not settings.LINE_CHANNEL_ACCESS_TOKEN:
                raise ValueError("LINE_CHANNEL_ACCESS_TOKEN not configured")
                
            configuration = Configuration(access_token=settings.LINE_CHANNEL_ACCESS_TOKEN)
            async_api_client = AsyncApiClient(configuration)
            self.line_bot_api = AsyncMessagingApi(async_api_client)
            print("✅ LINE Bot API initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize LINE Bot API: {e}")
            return False
    
    async def get_all_database_users(self, db: AsyncSession) -> List[UserStatus]:
        """Get all users from database"""
        try:
            result = await db.execute(select(UserStatus))
            users = result.scalars().all()
            print(f"📊 Found {len(users)} users in database")
            return users
        except Exception as e:
            print(f"❌ Error getting database users: {e}")
            return []
    
    async def get_existing_friend_activities(self, db: AsyncSession) -> Dict[str, datetime]:
        """Get existing friend activities to track what we already know"""
        try:
            result = await db.execute(
                select(FriendActivity.user_id, func.max(FriendActivity.timestamp))
                .where(FriendActivity.activity_type == 'follow')
                .group_by(FriendActivity.user_id)
            )
            activities = {user_id: timestamp for user_id, timestamp in result.fetchall()}
            print(f"📊 Found {len(activities)} existing friend activities")
            return activities
        except Exception as e:
            print(f"❌ Error getting friend activities: {e}")
            return {}
    
    async def check_user_friendship_status(self, user_id: str) -> Dict:
        """Check if user is still following the bot"""
        try:
            # Try to get user profile - if successful, user is still following
            profile = await self.line_bot_api.get_profile(user_id)
            if profile:
                return {
                    "is_friend": True,
                    "display_name": profile.display_name,
                    "picture_url": getattr(profile, 'picture_url', None),
                    "status_message": getattr(profile, 'status_message', None),
                    "language": getattr(profile, 'language', None),
                    "source": "line_api"
                }
        except Exception as e:
            # If we can't get profile, user likely unfollowed
            error_msg = str(e).lower()
            if "not found" in error_msg or "forbidden" in error_msg:
                return {"is_friend": False, "error": str(e)}
            else:
                # Other errors might be temporary
                return {"is_friend": "unknown", "error": str(e)}
        
        return {"is_friend": False, "error": "No profile returned"}
    
    async def sync_user_friend_status(self, db: AsyncSession, user: UserStatus, 
                                    existing_activities: Dict[str, datetime]) -> Dict:
        """Sync a single user's friend status"""
        user_id = user.user_id
        result = {
            "user_id": user_id,
            "action": "none",
            "changes": [],
            "error": None
        }
        
        try:
            # Check current friendship status
            friendship_status = await self.check_user_friendship_status(user_id)
            
            if friendship_status["is_friend"] == True:
                # User is currently following
                last_activity = existing_activities.get(user_id)
                
                # Check if this is a new friend (no previous follow activity)
                if not last_activity:
                    # New friend detected!
                    await self.handle_new_friend_detected(db, user_id, friendship_status)
                    result["action"] = "new_friend_detected"
                    result["changes"].append("Added to friend activity")
                    self.new_friends += 1
                
                # Update profile if needed
                if await self.update_user_profile_if_changed(db, user, friendship_status):
                    result["changes"].append("Profile updated")
                    self.updated_profiles += 1
            
            elif friendship_status["is_friend"] == False:
                # User unfollowed - record if we haven't already
                await self.handle_unfriend_detected(db, user_id, existing_activities)
                result["action"] = "unfriend_detected"
                result["changes"].append("Recorded unfollow")
            
            else:
                # Unknown status (API error)
                result["error"] = friendship_status.get("error", "Unknown error")
                self.errors += 1
        
        except Exception as e:
            result["error"] = str(e)
            self.errors += 1
            print(f"❌ Error syncing user {user_id}: {e}")
        
        return result
    
    async def handle_new_friend_detected(self, db: AsyncSession, user_id: str, profile_data: Dict):
        """Handle newly detected friend"""
        thai_time = get_thai_time()
        
        # Save friend activity
        await save_friend_activity(
            db=db, 
            user_id=user_id, 
            activity_type='follow',
            user_profile=profile_data,
            event_data={"detected_by": "friend_recheck_script", "timestamp": thai_time.isoformat()},
            source='manual_sync'
        )
        
        # Send Telegram notification
        await send_telegram_notification_enhanced(
            db=db,
            notification_type="new_friend_detected",
            title="🔍 เพื่อนใหม่ (ตรวจพบ)",
            message=f"ชื่อ: {profile_data.get('display_name', 'ไม่ทราบชื่อ')}\nUser ID: {user_id}\nตรวจพบจากการสแกนรายชื่อเพื่อน",
            user_id=user_id,
            priority=2,
            data={"user_profile": profile_data, "detection_method": "friend_recheck"}
        )
        
        # Log system event
        await log_system_event(
            db=db,
            level="info",
            category="friend_management",
            subcategory="new_friend_detected",
            message=f"New friend detected during recheck: {profile_data.get('display_name', user_id)}",
            user_id=user_id,
            details={"profile_data": profile_data}
        )
        
        print(f"🆕 New friend detected: {profile_data.get('display_name', user_id)} ({user_id})")
    
    async def handle_unfriend_detected(self, db: AsyncSession, user_id: str, 
                                     existing_activities: Dict[str, datetime]):
        """Handle detected unfriend"""
        # Only record if we haven't recorded an unfollow recently
        last_activity = existing_activities.get(user_id)
        if last_activity:
            # Check if we already have an unfollow record
            try:
                result = await db.execute(
                    select(FriendActivity)
                    .where(FriendActivity.user_id == user_id)
                    .where(FriendActivity.activity_type == 'unfollow')
                    .order_by(FriendActivity.timestamp.desc())
                    .limit(1)
                )
                recent_unfollow = result.scalar_one_or_none()
                
                if not recent_unfollow:
                    # Record the unfollow
                    thai_time = get_thai_time()
                    await save_friend_activity(
                        db=db,
                        user_id=user_id,
                        activity_type='unfollow',
                        user_profile={"user_id": user_id, "source": "unfollow_detection"},
                        event_data={"detected_by": "friend_recheck_script", "timestamp": thai_time.isoformat()},
                        source='manual_sync'
                    )
                    print(f"👋 Unfriend detected: {user_id}")
            except Exception as e:
                print(f"❌ Error checking unfollow status for {user_id}: {e}")
    
    async def update_user_profile_if_changed(self, db: AsyncSession, user: UserStatus, 
                                           profile_data: Dict) -> bool:
        """Update user profile if there are changes"""
        try:
            updated = False
            new_display_name = profile_data.get('display_name')
            new_picture_url = profile_data.get('picture_url')
            
            if new_display_name and new_display_name != user.display_name:
                user.display_name = new_display_name
                updated = True
            
            if new_picture_url and new_picture_url != user.picture_url:
                user.picture_url = new_picture_url
                updated = True
            
            if updated:
                await db.commit()
                print(f"📝 Updated profile for {user.user_id}: {new_display_name}")
            
            return updated
        except Exception as e:
            print(f"❌ Error updating profile for {user.user_id}: {e}")
            return False
    
    async def generate_summary_report(self, db: AsyncSession, results: List[Dict]):
        """Generate and send summary report"""
        thai_time = get_thai_time()
        
        # Create summary
        summary = f"""📊 สรุปการตรวจสอบรายชื่อเพื่อน
        
🕐 เวลา: {thai_time.strftime('%Y-%m-%d %H:%M:%S')}
👥 ผู้ใช้ทั้งหมด: {self.total_users}
🆕 เพื่อนใหม่: {self.new_friends}
📝 อัปเดตโปรไฟล์: {self.updated_profiles}
❌ ข้อผิดพลาด: {self.errors}

🔍 รายละเอียด:"""
        
        # Add details for new friends
        new_friend_details = []
        for result in results:
            if result["action"] == "new_friend_detected":
                new_friend_details.append(f"- {result['user_id']}")
        
        if new_friend_details:
            summary += f"\n\n🆕 เพื่อนใหม่ที่ตรวจพบ:\n" + "\n".join(new_friend_details[:10])
            if len(new_friend_details) > 10:
                summary += f"\n... และอีก {len(new_friend_details) - 10} คน"
        
        # Send summary to Telegram
        await send_telegram_notification_enhanced(
            db=db,
            notification_type="friend_check_summary",
            title="📊 สรุปการตรวจสอบเพื่อน",
            message=summary,
            priority=1,
            data={"stats": {
                "total_users": self.total_users,
                "new_friends": self.new_friends,
                "updated_profiles": self.updated_profiles,
                "errors": self.errors
            }}
        )
        
        print("📊 Summary report sent to Telegram")
    
    async def run_friend_check(self):
        """Main function to run the friend check"""
        print("🚀 Starting friend list recheck...")
        
        # Initialize LINE API
        if not await self.initialize_line_api():
            return False
        
        async with AsyncSessionLocal() as db:
            try:
                # Get all database users
                users = await self.get_all_database_users(db)
                self.total_users = len(users)
                
                if not users:
                    print("⚠️ No users found in database")
                    return True
                
                # Get existing friend activities
                existing_activities = await self.get_existing_friend_activities(db)
                
                # Process each user
                results = []
                for i, user in enumerate(users, 1):
                    print(f"⏳ Processing user {i}/{len(users)}: {user.user_id}")
                    
                    result = await self.sync_user_friend_status(db, user, existing_activities)
                    results.append(result)
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.1)
                
                # Generate summary report
                await self.generate_summary_report(db, results)
                
                print("✅ Friend list recheck completed successfully!")
                print(f"📊 Results: {self.new_friends} new friends, {self.updated_profiles} updated profiles, {self.errors} errors")
                
                return True
                
            except Exception as e:
                print(f"❌ Error during friend check: {e}")
                await log_system_event(
                    db=db,
                    level="error", 
                    category="friend_management",
                    subcategory="recheck_failed",
                    message=f"Friend recheck failed: {str(e)}",
                    details={"error": str(e)}
                )
                return False

async def main():
    """Main entry point"""
    checker = FriendListChecker()
    success = await checker.run_friend_check()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)