# PostgreSQL Database Configuration
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """PostgreSQL configuration for different environments"""
    
    @staticmethod
    def get_database_url(environment="development"):
        """Get database URL based on environment"""
        
        if environment == "development":
            # SQLite for local development
            return "sqlite+aiosqlite:///./chatbot.db"
        
        elif environment == "production":
            # PostgreSQL for production
            db_url = os.getenv("DATABASE_URL")
            
            # Handle Render.com PostgreSQL URL format
            if db_url and db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            
            return db_url or "postgresql+asyncpg://user:password@localhost/hrmoj"
        
        elif environment == "test":
            # PostgreSQL for testing
            return "postgresql+asyncpg://test:test@localhost/hrmoj_test"
    
    @staticmethod
    def get_engine_config(environment="development"):
        """Get engine configuration based on environment"""
        
        if environment == "development":
            return {
                "echo": True,  # Log SQL queries
                "pool_pre_ping": True,
            }
        
        elif environment == "production":
            return {
                "echo": False,
                "pool_size": 20,
                "max_overflow": 40,
                "pool_pre_ping": True,
                "pool_recycle": 3600,  # Recycle connections every hour
            }

# Create async engine
environment = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = DatabaseConfig.get_database_url(environment)
engine_config = DatabaseConfig.get_engine_config(environment)

# Create engine with appropriate configuration
if environment == "development":
    # SQLite doesn't support connection pooling well
    engine = create_async_engine(DATABASE_URL, **engine_config)
else:
    # PostgreSQL with connection pooling
    engine = create_async_engine(DATABASE_URL, **engine_config)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
