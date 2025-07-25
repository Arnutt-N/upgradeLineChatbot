# Telegram Service - Advanced Integration
import asyncio
import json
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.crud_enhanced import (
    get_pending_notifications, update_notification_status,
    get_telegram_setting, log_system_event
)

class TelegramService:
    """Advanced Telegram Bot Service"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.chat_id = settings.TELEGRAM_CHAT_ID
        self.api_base = f"https://api.telegram.org/bot{self.bot_token}"
        
    async def is_configured(self) -> bool:
        """ตรวจสอบว่า Telegram ตั้งค่าแล้วหรือยัง"""
        return bool(self.bot_token and self.chat_id)
    
    async def send_message(
        self, 
        message: str, 
        parse_mode: str = 'Markdown',
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """ส่งข้อความไป Telegram"""
        
        if not await self.is_configured():
            raise ValueError("Telegram not configured")
        
        url = f"{self.api_base}/sendMessage"
        data = {
            'chat_id': chat_id or self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data)
            response.raise_for_status()
            return response.json()
    
    async def send_notification_with_template(
        self,
        db: AsyncSession,
        template_key: str,
        data: Dict[str, Any],
        chat_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """ส่งการแจ้งเตือนโดยใช้ template"""
        
        # ดึง template จากฐานข้อมูล
        template = await get_telegram_setting(db, template_key)
        if not template:
            template = "แจ้งเตือน: {message}"
        
        # แทนที่ variables ใน template
        try:
            formatted_message = template.format(**data)
        except KeyError as e:
            formatted_message = f"แจ้งเตือน (Template Error): {data.get('message', 'N/A')}"
            await log_system_event(
                db=db,
                level="warning",
                category="telegram",
                subcategory="template_error",
                message=f"Template formatting error: {str(e)}",
                details={"template_key": template_key, "data": data}
            )
        
        return await self.send_message(formatted_message, chat_id=chat_id)
    
    async def process_notification_queue(self, db: AsyncSession) -> Dict[str, int]:
        """ประมวลผล queue การแจ้งเตือน"""
        
        if not await self.is_configured():
            return {"skipped": 0, "error": "not_configured"}
        
        # ดึงการแจ้งเตือนที่รอส่ง
        pending = await get_pending_notifications(db, limit=10)
        
        stats = {"sent": 0, "failed": 0, "skipped": 0}
        
        for notification in pending:
            try:
                # เตรียมข้อมูลสำหรับ template
                template_data = {
                    "title": notification.title,
                    "message": notification.message,
                    "user_name": "ไม่ระบุ",
                    "user_id": notification.user_id or "ไม่ระบุ",
                    "timestamp": notification.created_at.strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # เพิ่มข้อมูลจาก extra_data field
                if notification.extra_data:
                    try:
                        extra_data = json.loads(notification.extra_data)
                        template_data.update(extra_data)
                        
                        # ดึงชื่อจาก user_profile ถ้ามี
                        if 'user_profile' in extra_data:
                            profile = extra_data['user_profile']
                            template_data['user_name'] = profile.get('display_name', 'ไม่ระบุ')
                    except json.JSONDecodeError:
                        pass
                
                # กำหนด template key ตาม notification type
                template_mapping = {
                    "chat_request": "chat_request_template",
                    "new_friend": "new_friend_template", 
                    "friend_left": "new_friend_template",
                    "system_alert": "system_alert_template"
                }
                
                template_key = template_mapping.get(
                    notification.notification_type, 
                    "chat_request_template"
                )
                
                # ส่งข้อความ
                result = await self.send_notification_with_template(
                    db=db,
                    template_key=template_key,
                    data=template_data,
                    chat_id=notification.telegram_chat_id
                )
                
                # อัพเดทสถานะเป็น sent
                await update_notification_status(
                    db=db,
                    notification_id=notification.id,
                    status='sent',
                    telegram_message_id=result.get('result', {}).get('message_id')
                )
                
                stats["sent"] += 1
                
                await log_system_event(
                    db=db,
                    level="info",
                    category="telegram",
                    subcategory="notification_sent",
                    message=f"Notification sent: {notification.notification_type}",
                    details={
                        "notification_id": notification.id,
                        "telegram_message_id": result.get('result', {}).get('message_id')
                    }
                )
                
            except Exception as e:
                # อัพเดทสถานะเป็น failed
                await update_notification_status(
                    db=db,
                    notification_id=notification.id,
                    status='failed',
                    error_message=str(e)
                )
                
                stats["failed"] += 1
                
                await log_system_event(
                    db=db,
                    level="error",
                    category="telegram",
                    subcategory="notification_failed",
                    message=f"Failed to send notification: {str(e)}",
                    details={
                        "notification_id": notification.id,
                        "error": str(e),
                        "notification_type": notification.notification_type
                    }
                )
            
            # หน่วงเวลาเล็กน้อยระหว่างการส่ง
            await asyncio.sleep(0.5)
        
        return stats
    
    async def get_bot_info(self) -> Dict[str, Any]:
        """ดึงข้อมูล Bot"""
        
        if not await self.is_configured():
            raise ValueError("Telegram not configured")
        
        url = f"{self.api_base}/getMe"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def test_connection(self, db: AsyncSession) -> Dict[str, Any]:
        """ทดสอบการเชื่อมต่อ Telegram"""
        
        try:
            if not await self.is_configured():
                return {
                    "success": False,
                    "error": "not_configured",
                    "message": "Telegram credentials not configured"
                }
            
            # ทดสอบ getMe
            bot_info = await self.get_bot_info()
            
            # ทดสอบส่งข้อความ
            test_message = f"🧪 **Test Connection**\n\nBot: {bot_info['result']['first_name']}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            send_result = await self.send_message(test_message)
            
            # Log การทดสอบ
            await log_system_event(
                db=db,
                level="info",
                category="telegram",
                subcategory="connection_test",
                message="Telegram connection test successful",
                details={
                    "bot_info": bot_info['result'],
                    "test_message_id": send_result.get('result', {}).get('message_id')
                }
            )
            
            return {
                "success": True,
                "bot_info": bot_info['result'],
                "test_message_sent": True,
                "message_id": send_result.get('result', {}).get('message_id')
            }
            
        except Exception as e:
            await log_system_event(
                db=db,
                level="error", 
                category="telegram",
                subcategory="connection_test_failed",
                message=f"Telegram connection test failed: {str(e)}",
                details={"error": str(e)}
            )
            
            return {
                "success": False,
                "error": str(e),
                "message": "Connection test failed"
            }

# ========================================
# Background Task for Processing Queue
# ========================================

class TelegramQueueProcessor:
    """Background processor สำหรับ Telegram queue"""
    
    def __init__(self, telegram_service: TelegramService):
        self.telegram_service = telegram_service
        self.is_running = False
        
    async def start(self, db: AsyncSession, interval: int = 30):
        """เริ่ม background processing"""
        
        if self.is_running:
            return
        
        self.is_running = True
        
        await log_system_event(
            db=db,
            level="info",
            category="telegram",
            subcategory="queue_processor_started",
            message=f"Telegram queue processor started (interval: {interval}s)"
        )
        
        while self.is_running:
            try:
                stats = await self.telegram_service.process_notification_queue(db)
                
                if stats.get("sent", 0) > 0 or stats.get("failed", 0) > 0:
                    await log_system_event(
                        db=db,
                        level="info",
                        category="telegram",
                        subcategory="queue_processed",
                        message="Telegram queue processed",
                        details=stats
                    )
                
            except Exception as e:
                await log_system_event(
                    db=db,
                    level="error",
                    category="telegram", 
                    subcategory="queue_processor_error",
                    message=f"Queue processor error: {str(e)}",
                    details={"error": str(e)}
                )
            
            await asyncio.sleep(interval)
    
    def stop(self):
        """หยุด background processing"""
        self.is_running = False

# ========================================
# Global Instance
# ========================================

telegram_service = TelegramService()
queue_processor = TelegramQueueProcessor(telegram_service)

# Export
__all__ = [
    'TelegramService',
    'TelegramQueueProcessor', 
    'telegram_service',
    'queue_processor'
]
