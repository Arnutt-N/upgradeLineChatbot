# app/db/database_postgres.py
"""
PostgreSQL Database Configuration for Production
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.db.models import Base

def get_database_config():
    """Get database configuration based on environment"""
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    if DB_TYPE == "postgresql" and DATABASE_URL:
        # PostgreSQL configuration for production
        if DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        print(f"🐘 Using PostgreSQL for {ENVIRONMENT}")
        
        engine = create_async_engine(
            DATABASE_URL,
            echo=(ENVIRONMENT == "development"),
            poolclass=NullPool,  # Recommended for serverless environments
            connect_args={
                "server_settings": {"jit": "off"},
                "command_timeout": 60,
            }
        )
    else:
        # SQLite fallback for development
        print(f"🗄️ Using SQLite for {ENVIRONMENT}")
        SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"
        engine = create_async_engine(
            SQLALCHEMY_DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    
    return engine

# Create engine
engine = get_database_config()

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
