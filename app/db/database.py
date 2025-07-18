# app/db/database.py
"""
Database configuration - Force SQLite for production deployment
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# FORCE SQLite configuration regardless of environment variables
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"

print(f"🗄️ FORCED SQLite Database: {SQLALCHEMY_DATABASE_URL}")

# Create SQLite engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # Set to True for debugging
)

# Create session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    """Database dependency for FastAPI"""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_db_and_tables():
    """Create database tables"""
    print("📦 Creating SQLite database tables...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ SQLite database tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

# Health check function
async def check_database_health():
    """Check if database is accessible"""
    try:
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("SELECT 1"))
            return result.scalar() == 1
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False
