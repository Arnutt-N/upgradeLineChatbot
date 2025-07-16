# PostgreSQL Migration Script
"""
Migration script to convert from SQLite to PostgreSQL
Run this script to migrate existing data
"""

import asyncio
import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg
from dotenv import load_dotenv

load_dotenv()

async def create_postgresql_database():
    """Create PostgreSQL database if not exists"""
    
    # Parse database URL
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost/hrmoj")
    
    # Extract connection parameters
    if db_url.startswith("postgresql://"):
        conn_str = db_url[13:]  # Remove postgresql://
        user_pass, host_db = conn_str.split('@')
        
        if ':' in user_pass:
            user, password = user_pass.split(':')
        else:
            user, password = user_pass, ''
            
        host_port, db_name = host_db.split('/')
        
        if ':' in host_port:
            host, port = host_port.split(':')
        else:
            host, port = host_port, '5432'
    
    # Connect to PostgreSQL server (not specific database)
    try:
        conn = await asyncpg.connect(
            user=user,
            password=password,
            host=host,
            port=port,
            database='postgres'  # Connect to default database
        )
        
        # Check if database exists
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name
        )
        
        if not exists:
            # Create database
            await conn.execute(f'CREATE DATABASE {db_name}')
            print(f"✅ Created database: {db_name}")
        else:
            print(f"ℹ️ Database already exists: {db_name}")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        raise

async def migrate_sqlite_to_postgresql():
    """Migrate data from SQLite to PostgreSQL"""
    
    print("🚀 Starting SQLite to PostgreSQL migration...")
    
    # Create PostgreSQL database
    await create_postgresql_database()
    
    # Import models
    from app.db.postgresql.models_postgres import Base, create_tables
    from app.db.postgresql.database_config import DATABASE_URL
    
    # Create PostgreSQL engine
    pg_engine = create_async_engine(DATABASE_URL)
    
    # Create tables
    async with pg_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ PostgreSQL tables created")
    
    # TODO: Add data migration logic here
    # 1. Connect to SQLite
    # 2. Read data from each table
    # 3. Transform data if needed
    # 4. Insert into PostgreSQL
    
    await pg_engine.dispose()
    print("✅ Migration completed!")

if __name__ == "__main__":
    asyncio.run(migrate_sqlite_to_postgresql())
