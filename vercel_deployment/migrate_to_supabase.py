# migrate_to_supabase.py - Migration script for Supabase PostgreSQL
import asyncio
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text

# Load environment variables
load_dotenv('.env.production')

async def test_connection():
    """Test Supabase connection"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env.production")
        return False
    
    # Convert to asyncpg URL format
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"🔄 Testing connection to Supabase...")
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
            return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()

async def create_tables():
    """Create all required tables in Supabase"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        # Import models to ensure they're registered
        from app.db.postgresql.models_postgres import Base
        
        async with engine.begin() as conn:
            print("📦 Creating tables in Supabase...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully!")
            
            # List created tables
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            print(f"📋 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise
    finally:
        await engine.dispose()

async def migrate_from_sqlite():
    """Migrate data from SQLite to Supabase"""
    print("\n🚀 Starting data migration from SQLite to Supabase...")
    
    # Setup SQLite connection
    sqlite_engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db", echo=False)
    sqlite_session = sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Setup PostgreSQL connection
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    pg_engine = create_async_engine(DATABASE_URL, echo=False)
    pg_session = sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # Import models
        from app.db.models import UserStatus as SQLiteUserStatus, ChatMessage as SQLiteChatMessage
        from app.db.postgresql.models_postgres import UserStatus as PGUserStatus, ChatMessage as PGChatMessage
        
        # Migrate UserStatus
        print("\n📋 Migrating user_status table...")
        async with sqlite_session() as source, pg_session() as target:
            # Read from SQLite
            result = await source.execute(select(SQLiteUserStatus))
            users = result.scalars().all()
            
            # Write to PostgreSQL
            for user in users:
                pg_user = PGUserStatus(
                    user_id=user.user_id,
                    display_name=user.display_name,
                    picture_url=user.picture_url,
                    is_in_live_chat=user.is_in_live_chat,
                    chat_mode=user.chat_mode
                )
                target.add(pg_user)
            
            await target.commit()
            print(f"✅ Migrated {len(users)} users")
        
        # Migrate ChatMessages (last 1000 messages)
        print("\n📋 Migrating chat_messages table...")
        async with sqlite_session() as source, pg_session() as target:
            # Read from SQLite
            result = await source.execute(
                select(SQLiteChatMessage)
                .order_by(SQLiteChatMessage.created_at.desc())
                .limit(1000)
            )
            messages = result.scalars().all()
            
            # Write to PostgreSQL
            for msg in messages:
                pg_msg = PGChatMessage(
                    id=msg.id,
                    user_id=msg.user_id,
                    sender_type=msg.sender_type,
                    message=msg.message,
                    created_at=msg.created_at
                )
                target.add(pg_msg)
            
            await target.commit()
            print(f"✅ Migrated {len(messages)} messages")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        raise
    finally:
        await sqlite_engine.dispose()
        await pg_engine.dispose()

async def verify_migration():
    """Verify migrated data"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        async with engine.connect() as conn:
            # Count records
            user_count = await conn.execute(text("SELECT COUNT(*) FROM user_status"))
            message_count = await conn.execute(text("SELECT COUNT(*) FROM chat_messages"))
            
            print("\n📊 Migration Summary:")
            print(f"  - Users: {user_count.scalar()}")
            print(f"  - Messages: {message_count.scalar()}")
            
            # Sample data
            print("\n📋 Sample migrated data:")
            result = await conn.execute(text("""
                SELECT user_id, display_name, chat_mode 
                FROM user_status 
                LIMIT 5
            """))
            for row in result:
                print(f"  - User: {row[0]}, Name: {row[1]}, Mode: {row[2]}")
                
    finally:
        await engine.dispose()

async def main():
    """Main migration process"""
    print("🚀 Supabase PostgreSQL Migration Tool")
    print("=====================================\n")
    
    # Step 1: Test connection
    if not await test_connection():
        return
    
    print("\n" + "="*50 + "\n")
    
    # Step 2: Create tables
    await create_tables()
    
    print("\n" + "="*50 + "\n")
    
    # Step 3: Ask for confirmation before migrating data
    if os.path.exists("chatbot.db"):
        response = input("\n📦 SQLite database found. Migrate data to Supabase? (y/n): ")
        if response.lower() == 'y':
            await migrate_from_sqlite()
            await verify_migration()
    else:
        print("ℹ️ No SQLite database found. Tables created empty.")
    
    print("\n✅ All done! Your Supabase database is ready.")
    print("\n📌 Next steps:")
    print("  1. Update your .env file with the PostgreSQL URL")
    print("  2. Set ENVIRONMENT=production")
    print("  3. Deploy to Vercel")
    print("  4. Update LINE webhook URL to your Vercel domain")

if __name__ == "__main__":
    asyncio.run(main())
