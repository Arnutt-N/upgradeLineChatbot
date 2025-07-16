# app/db/database.py
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings

# Import the proper database configuration based on environment
if os.getenv("ENVIRONMENT") == "production":
    from app.db.postgresql.database_config import engine as configured_engine, get_db as configured_get_db
    from app.db.postgresql.models_postgres import Base
else:
    from app.db.postgresql.database_config import engine as configured_engine, get_db as configured_get_db
    from app.db.models import Base

# สร้างโฟลเดอร์สำหรับ database ถ้ายังไม่มี (สำหรับ SQLite)
def ensure_database_directory():
    """สร้างโฟลเดอร์สำหรับ database"""
    if settings.DATABASE_URL.startswith('sqlite'):
        # Extract database path from URL
        db_path = settings.DATABASE_URL.replace('sqlite+aiosqlite:///', '')
        db_dir = Path(db_path).parent
        
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        db_dir.mkdir(parents=True, exist_ok=True)
        print(f"Ensured database directory exists: {db_dir}")

# เรียกใช้ฟังก์ชันสร้างโฟลเดอร์
ensure_database_directory()

# ใช้ configured engine จาก database_config.py
async_engine = configured_engine

# สร้าง async session (ใช้จากการกำหนดค่าที่ถูกต้อง)
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def create_db_and_tables():
    """สร้างตารางฐานข้อมูล"""
    async with async_engine.begin() as conn:
        # สร้างตารางทั้งหมด (รวมตารางใหม่สำหรับ Forms System)
        await conn.run_sync(Base.metadata.create_all)
        print("All database tables created successfully")
        
        # เพิ่ม column chat_mode ถ้ายังไม่มี (สำหรับ database เก่า)
        try:
            await conn.execute(text("ALTER TABLE user_status ADD COLUMN chat_mode VARCHAR DEFAULT 'manual'"))
            print("Added chat_mode column to user_status table")
        except Exception as e:
            # Column อาจมีอยู่แล้วหรือเกิด error อื่น
            print(f"Note: chat_mode column already exists or error: {e}")
            pass
        
        # เพิ่ม column picture_url ถ้ายังไม่มี (สำหรับ avatar feature)
        try:
            await conn.execute(text("ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL"))
            print("Added picture_url column to user_status table")
        except Exception as e:
            # Column อาจมีอยู่แล้วหรือเกิด error อื่น
            print(f"Note: picture_url column already exists or error: {e}")
            pass
            
        print("Database migration completed successfully!")

_db_initialized = False

async def ensure_db_initialized():
    """Ensure database is initialized (lazy initialization)"""
    global _db_initialized
    if not _db_initialized:
        try:
            await create_db_and_tables()
            _db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Continue without marking as initialized so it will retry

async def get_db():
    """Dependency สำหรับรับ database session"""
    await ensure_db_initialized()
    # ใช้ configured get_db function
    async for session in configured_get_db():
        yield session
