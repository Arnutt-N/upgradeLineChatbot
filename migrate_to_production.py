# migrate_to_production.py
"""
Production Migration Script for Render + Supabase PostgreSQL
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

print("🔧 Loading application modules...")
try:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    from app.db.models import Base
    print("✅ Application modules loaded successfully")
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)

async def test_database_connection(engine):
    """Test the database connection"""
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version[:50]}...")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def create_tables(engine):
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            print("📦 Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully!")
            return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
async def migrate_to_production():
    """Main migration function"""
    print("🚀 Starting production database migration...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    print(f"Environment: {ENVIRONMENT}")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    # Convert PostgreSQL URL for asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        print("🔄 Converted to asyncpg URL format")
    
    # Create engine with production settings
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        connect_args={
            "server_settings": {"jit": "off"},
            "command_timeout": 60,
        }
    )
    
    try:
        # Test connection
        print("Testing database connection...")
        if not await test_database_connection(engine):
            return False
        
        # Create tables
        print("Creating database tables...")
        if not await create_tables(engine):
            return False
        
        print("🎉 Production migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"💥 Migration failed with error: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(migrate_to_production())
    sys.exit(0 if success else 1)
