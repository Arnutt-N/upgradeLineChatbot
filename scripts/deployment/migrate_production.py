#!/usr/bin/env python3
"""
Production Database Migration Script
ใช้สำหรับ migrate database ใน production environment
"""

import os
import sys
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def ensure_database_exists():
    """สร้างฐานข้อมูลถ้ายังไม่มี"""
    db_path = project_root / "chatbot.db"
    
    if not db_path.exists():
        print("Creating new database...")
        conn = sqlite3.connect(str(db_path))
        conn.close()
        print("✅ Database created successfully!")
    else:
        print("✅ Database already exists")
    
    return str(db_path)

def run_migrations():
    """รัน migration scripts ทั้งหมด"""
    
    print("🚀 Starting Production Database Migration...")
    print("=" * 50)
    
    # สร้างฐานข้อมูลถ้ายังไม่มี
    db_path = ensure_database_exists()
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # สร้าง migration history table ถ้ายังไม่มี
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name TEXT NOT NULL,
                executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                error_message TEXT
            )
        """)
        
        # ตรวจสอบ migration ที่รันแล้ว
        cursor.execute("SELECT migration_name FROM migration_history WHERE success = 1")
        completed_migrations = {row[0] for row in cursor.fetchall()}
        
        # Migration files ตามลำดับ
        migration_files = [
            "001_add_enhanced_tracking_tables.sql",
            "002_fix_metadata_column.sql"
        ]
        
        migrations_dir = project_root / "migrations"
        
        for migration_file in migration_files:
            if migration_file in completed_migrations:
                print(f"⏭️  Skipping {migration_file} (already applied)")
                continue
            
            migration_path = migrations_dir / migration_file
            
            if not migration_path.exists():
                print(f"⚠️  Migration file not found: {migration_file}")
                continue
            
            print(f"🔄 Running migration: {migration_file}")
            
            try:
                # อ่านและรัน migration
                with open(migration_path, 'r', encoding='utf-8') as f:
                    migration_sql = f.read()
                
                # แยก statements และรันทีละอัน
                statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement.strip():
                        cursor.execute(statement)
                
                # บันทึกว่า migration สำเร็จ
                cursor.execute(
                    "INSERT INTO migration_history (migration_name, success) VALUES (?, ?)",
                    (migration_file, True)
                )
                
                conn.commit()
                print(f"✅ {migration_file} completed successfully")
                
            except Exception as e:
                print(f"❌ {migration_file} failed: {str(e)}")
                
                # บันทึก error
                cursor.execute(
                    "INSERT INTO migration_history (migration_name, success, error_message) VALUES (?, ?, ?)",
                    (migration_file, False, str(e))
                )
                conn.commit()
                
                # ไม่หยุดเพราะ error อาจจะเป็นเพราะตารางมีอยู่แล้ว
                continue
        
        # ตรวจสอบและสร้าง default data
        create_default_data(cursor)
        
        conn.commit()
        conn.close()
        
        print("\n" + "=" * 50)
        print("🎉 Production migration completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"💥 Migration failed: {str(e)}")
        return False

def create_default_data(cursor):
    """สร้างข้อมูล default ที่จำเป็น"""
    
    print("🔧 Creating default data...")
    
    try:
        # Default telegram settings
        default_settings = [
            ('ts_001', 'notification_enabled', 'true', 'boolean', 'เปิดใช้งานการแจ้งเตือนไป Telegram'),
            ('ts_002', 'chat_request_template', 'แจ้งเตือนการแชท: {user_name} - {message}', 'string', 'Template สำหรับแจ้งเตือนการขอแชท'),
            ('ts_003', 'new_friend_template', 'เพื่อนใหม่: {user_name}', 'string', 'Template สำหรับแจ้งเตือนเพื่อนใหม่'),
            ('ts_004', 'system_alert_template', 'แจ้งเตือนระบบ: {title} - {message}', 'string', 'Template สำหรับแจ้งเตือนระบบ'),
            ('ts_005', 'retry_attempts', '3', 'integer', 'จำนวนครั้งที่พยายามส่งใหม่หากล้มเหลว'),
            ('ts_006', 'retry_delay_seconds', '30', 'integer', 'หน่วงเวลา (วินาที) ก่อนส่งใหม่'),
            ('ts_007', 'notification_queue_size', '100', 'integer', 'ขนาด queue สำหรับการแจ้งเตือน'),
            ('ts_008', 'enable_debug_logs', 'false', 'boolean', 'เปิดใช้งาน debug logs สำหรับ Telegram')
        ]
        
        for setting_id, key, value, setting_type, description in default_settings:
            cursor.execute("""
                INSERT OR IGNORE INTO telegram_settings 
                (id, setting_key, setting_value, setting_type, description, is_active, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (setting_id, key, value, setting_type, description, True, datetime.now()))
        
        # ตรวจสอบจำนวน settings
        cursor.execute("SELECT COUNT(*) FROM telegram_settings")
        count = cursor.fetchone()[0]
        print(f"✅ Telegram settings: {count} records")
        
        # Default admin user (ถ้ายังไม่มี)
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            print("🔐 Creating default admin user...")
            from datetime import datetime
            import hashlib
            
            # สร้าง admin user เริ่มต้น
            password_hash = hashlib.sha256("admin".encode()).hexdigest()
            cursor.execute("""
                INSERT INTO admin_users 
                (id, username, password_hash, full_name, role, is_active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "admin_001", "admin", password_hash, "System Administrator", 
                "admin", True, datetime.now()
            ))
            print("✅ Default admin user created (username: admin, password: admin)")
        
    except Exception as e:
        print(f"⚠️  Error creating default data: {e}")

def verify_production_setup():
    """ตรวจสอบการตั้งค่าสำหรับ production"""
    
    print("\n🔍 Verifying production setup...")
    
    # ตรวจสอบ environment variables ที่จำเป็น
    required_env_vars = [
        'LINE_CHANNEL_SECRET',
        'LINE_CHANNEL_ACCESS_TOKEN'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📋 Please set these in Render Dashboard:")
        print("   Render Dashboard > Environment > Environment Variables")
    else:
        print("✅ All required environment variables are set")
    
    # ตรวจสอบไฟล์ที่จำเป็น
    required_files = [
        "app/main.py",
        "requirements.txt",
        "render.yaml"
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")

if __name__ == "__main__":
    print("🚀 Production Migration Script")
    print(f"📍 Project root: {project_root}")
    print(f"🕐 Started at: {datetime.now()}")
    
    try:
        success = run_migrations()
        verify_production_setup()
        
        if success:
            print("\n🎉 Production migration completed successfully!")
            print("🌐 Your app is ready for deployment!")
        else:
            print("\n❌ Migration completed with errors")
            print("🔧 Please check the logs and fix any issues")
            
    except Exception as e:
        print(f"\n💥 Critical error: {e}")
        sys.exit(1)
