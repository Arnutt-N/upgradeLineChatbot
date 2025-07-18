#!/usr/bin/env python3
"""
Test both SQLite and PostgreSQL database modes
ทดสอบทั้ง SQLite และ PostgreSQL database modes
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_development_mode():
    """ทดสอบโหมด Development (SQLite)"""
    print("\n=== TESTING DEVELOPMENT MODE (SQLite) ===")
    
    # Force development mode
    os.environ['ENVIRONMENT'] = 'development'
    
    try:
        from app.db.postgresql.database_config import DatabaseConfig, get_db
        
        env = os.getenv('ENVIRONMENT')
        db_url = DatabaseConfig.get_database_url(env)
        print(f"Environment: {env}")
        print(f"Database URL: {db_url}")
        
        # Test SQLite models
        from app.db.models import UserStatus, ChatMessage
        print(f"Models loaded: UserStatus, ChatMessage")
        
        # Test connection
        async for session in get_db():
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test"))
            test_result = result.scalar()
            print(f"SQLite test query result: {test_result}")
            break
            
        print("SUCCESS: SQLite (development) mode working correctly!")
        
    except Exception as e:
        print(f"ERROR in development mode: {e}")

async def test_production_mode():
    """ทดสอบโหมด Production (PostgreSQL)"""
    print("\n=== TESTING PRODUCTION MODE (PostgreSQL) ===")
    
    # Force production mode
    os.environ['ENVIRONMENT'] = 'production'
    
    try:
        from app.db.postgresql.database_config import DatabaseConfig
        
        env = os.getenv('ENVIRONMENT')
        db_url = DatabaseConfig.get_database_url(env)
        print(f"Environment: {env}")
        print(f"Database URL: {db_url}")
        
        # Test PostgreSQL models
        from app.db.postgresql.models_postgres import UserStatus, ChatMessage
        print(f"PostgreSQL models loaded: UserStatus, ChatMessage")
        
        print("SUCCESS: PostgreSQL (production) mode configuration ready!")
        
    except Exception as e:
        print(f"ERROR in production mode: {e}")

async def test_crud_imports():
    """ทดสอบการ import ใน CRUD"""
    print("\n=== TESTING CRUD IMPORTS ===")
    
    # Test development mode imports
    os.environ['ENVIRONMENT'] = 'development'
    try:
        from app.db.crud import get_or_create_user_status
        print("SUCCESS: CRUD imports working in development mode")
    except Exception as e:
        print(f"ERROR in CRUD development imports: {e}")
    
    # Test production mode imports
    os.environ['ENVIRONMENT'] = 'production'
    try:
        # Clear imports cache
        import importlib
        import app.db.crud
        importlib.reload(app.db.crud)
        
        from app.db.crud import get_or_create_user_status
        print("SUCCESS: CRUD imports working in production mode")
    except Exception as e:
        print(f"ERROR in CRUD production imports: {e}")

async def main():
    """รันการทดสอบทั้งหมด"""
    print("Testing AI Agent น้อง HR Moj Database Modes")
    print("=" * 50)
    
    await test_development_mode()
    await test_production_mode()
    await test_crud_imports()
    
    print("\n" + "=" * 50)
    print("Database mode testing completed!")
    print("INFO: System is ready for PostgreSQL migration")

if __name__ == "__main__":
    asyncio.run(main())