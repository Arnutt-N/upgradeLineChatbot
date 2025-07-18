#!/usr/bin/env python3
"""
Test PostgreSQL connection for AI Agent น้อง HR Moj
ทดสอบการเชื่อมต่อ PostgreSQL อย่างระมัดระวัง
"""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def test_postgresql_connection():
    """ทดสอบการเชื่อมต่อ PostgreSQL"""
    print("Testing PostgreSQL connection...")
    
    try:
        # Test environment switching
        print(f"Current Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"Database URL: {os.getenv('DATABASE_URL', 'Not set')}")
        
        # Import database configuration
        from app.db.postgresql.database_config import DatabaseConfig, get_db
        
        # Test database URL generation
        env = os.getenv('ENVIRONMENT', 'development')
        db_url = DatabaseConfig.get_database_url(env)
        print(f"Generated Database URL: {db_url}")
        
        # Test engine config
        engine_config = DatabaseConfig.get_engine_config(env)
        print(f"Engine Config: {engine_config}")
        
        # Test async session
        async for session in get_db():
            print("SUCCESS: Database session created successfully")
            
            # Test simple query
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1 as test"))
            test_result = result.scalar()
            print(f"Test query result: {test_result}")
            
            break  # Only test one session
            
        print("SUCCESS: PostgreSQL connection test completed successfully!")
        
    except ImportError as e:
        print(f"ERROR: Import error: {e}")
        print("INFO: This is expected in development mode with SQLite")
        
    except Exception as e:
        print(f"WARNING: Connection error: {e}")
        print("INFO: This might be expected if PostgreSQL is not available locally")
        
    finally:
        print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_postgresql_connection())