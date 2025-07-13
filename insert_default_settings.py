#!/usr/bin/env python3
"""
Insert Default Settings to Database
"""

import sqlite3
import uuid
from datetime import datetime

def insert_default_settings():
    """Insert default Telegram settings"""
    print("Inserting default Telegram settings...")
    
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # Default Telegram settings
        settings = [
            ('ts_001', 'notification_enabled', 'true', 'boolean', 'เปิดใช้งานการแจ้งเตือนไป Telegram'),
            ('ts_002', 'chat_request_template', 'แจ้งเตือนการแชท: {user_name} - {message}', 'string', 'Template สำหรับแจ้งเตือนการขอแชท'),
            ('ts_003', 'new_friend_template', 'เพื่อนใหม่: {user_name}', 'string', 'Template สำหรับแจ้งเตือนเพื่อนใหม่'),
            ('ts_004', 'system_alert_template', 'แจ้งเตือนระบบ: {title} - {message}', 'string', 'Template สำหรับแจ้งเตือนระบบ'),
            ('ts_005', 'retry_attempts', '3', 'integer', 'จำนวนครั้งที่พยายามส่งใหม่หากล้มเหลว'),
            ('ts_006', 'retry_delay_seconds', '30', 'integer', 'หน่วงเวลา (วินาที) ก่อนส่งใหม่'),
            ('ts_007', 'notification_queue_size', '100', 'integer', 'ขนาด queue สำหรับการแจ้งเตือน'),
            ('ts_008', 'enable_debug_logs', 'false', 'boolean', 'เปิดใช้งาน debug logs สำหรับ Telegram')
        ]
        
        inserted_count = 0
        for setting_id, key, value, setting_type, description in settings:
            cursor.execute("""
                INSERT OR IGNORE INTO telegram_settings 
                (id, setting_key, setting_value, setting_type, description, is_active, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (setting_id, key, value, setting_type, description, True, datetime.now()))
            
            if cursor.rowcount > 0:
                inserted_count += 1
                print(f"Inserted setting: {key}")
        
        conn.commit()
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM telegram_settings")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"Total settings in database: {total_count}")
        print(f"New settings inserted: {inserted_count}")
        print("Default settings insertion completed!")
        
        return True
        
    except Exception as e:
        print(f"Error inserting default settings: {str(e)}")
        return False

if __name__ == "__main__":
    success = insert_default_settings()
    if success:
        print("Settings insertion successful!")
    else:
        print("Settings insertion failed!")
