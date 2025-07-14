# app/db/database.py
import os
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.core.config import settings
from app.db.models import Base

# สร้างโฟลเดอร์สำหรับ database ถ้ายังไม่มี
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

# สร้าง async engine
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Disable SQL logging to prevent startup hanging
    future=True
)

# สร้าง async session
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
    async with AsyncSessionLocal() as session:
        yield session
