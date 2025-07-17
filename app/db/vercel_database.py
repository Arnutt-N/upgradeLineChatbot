# app/db/vercel_database.py
"""
Optimized database configuration for Vercel serverless environment
"""
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VercelDatabaseConfig:
    """Database configuration optimized for Vercel"""
    
    @staticmethod
    def get_database_url():
        """Get database URL with proper formatting"""
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            raise ValueError("DATABASE_URL not found in environment variables")
        
        # Convert postgres:// to postgresql+asyncpg://
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Ensure SSL mode for Supabase
        if "supabase.co" in db_url and "sslmode=" not in db_url:
            db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
        
        return db_url
    
    @staticmethod
    def create_engine():
        """Create SQLAlchemy engine optimized for serverless"""
        database_url = VercelDatabaseConfig.get_database_url()
        
        # Serverless-optimized settings
        return create_async_engine(
            database_url,
            # Use NullPool for serverless to avoid connection issues
            poolclass=NullPool,
            # Echo SQL only in development
            echo=os.getenv("ENVIRONMENT") != "production",
            # Connection arguments
            connect_args={
                "server_settings": {
                    "application_name": "linechatbot-vercel",
                    "jit": "off"
                },
                "command_timeout": 10,
                "timeout": 10,
            }
        )

# Create engine and session factory
engine = VercelDatabaseConfig.create_engine()

# Async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependency for FastAPI
async def get_db():
    """Get database session for FastAPI dependency injection"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise
        finally:
            await session.close()

# Database initialization
async def init_database():
    """Initialize database tables"""
    try:
        # Import models based on environment
        if os.getenv("DB_TYPE") == "postgresql":
            from app.db.postgresql.models_postgres import Base
        else:
            from app.db.models import Base
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables initialized")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        # Don't raise - let the app start anyway
        # Tables might already exist

# Health check function
async def check_database_health():
    """Check database connectivity"""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
            return True
    except Exception:
        return False
