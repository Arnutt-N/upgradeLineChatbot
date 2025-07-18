# Migrate SQLite to PostgreSQL
import asyncio
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
import sys

# Add project root to path
sys.path.append('.')

from app.db.models import Base, UserStatus, ChatHistory, FriendActivity, TelegramNotification

async def create_postgresql_tables():
    """Create all tables in PostgreSQL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        print("💡 Set it using: export DATABASE_URL='postgresql://...'")
        return False
    
    # Convert to asyncpg URL
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"🔄 Connecting to PostgreSQL...")
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # Test connection
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to: {version}")
        
        # Create tables
        async with engine.begin() as conn:
            print("📦 Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully!")
            
        # List created tables
        async with engine.connect() as conn:
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"\n📋 Created tables: {', '.join(tables)}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await engine.dispose()

async def migrate_data():
    """Migrate data from SQLite to PostgreSQL"""
    # SQLite connection
    sqlite_engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db", echo=False)
    sqlite_session = sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
    
    # PostgreSQL connection
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    pg_engine = create_async_engine(DATABASE_URL, echo=False)
    pg_session = sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        # Migrate UserStatus
        print("\n📤 Migrating UserStatus...")
        async with sqlite_session() as source, pg_session() as target:
            result = await source.execute(select(UserStatus))
            users = result.scalars().all()
            
            for user in users:
                # Check if user exists
                existing = await target.get(UserStatus, user.user_id)
                if not existing:
                    new_user = UserStatus(
                        user_id=user.user_id,
                        display_name=user.display_name,
                        picture_url=user.picture_url,
                        is_in_live_chat=user.is_in_live_chat,
                        chat_mode=user.chat_mode,
                        created_at=user.created_at,
                        updated_at=user.updated_at
                    )
                    target.add(new_user)
            
            await target.commit()
            print(f"✅ Migrated {len(users)} users")
        
        # Migrate ChatHistory (recent 1000 messages)
        print("\n📤 Migrating ChatHistory...")
        async with sqlite_session() as source, pg_session() as target:
            result = await source.execute(
                select(ChatHistory)
                .order_by(ChatHistory.timestamp.desc())
                .limit(1000)
            )
            messages = result.scalars().all()
            
            for msg in messages:
                # Check if message exists
                existing = await target.get(ChatHistory, msg.id)
                if not existing:
                    new_msg = ChatHistory(
                        id=msg.id,
                        user_id=msg.user_id,
                        message_type=msg.message_type,
                        message_content=msg.message_content,
                        admin_user_id=msg.admin_user_id,
                        is_read=msg.is_read,
                        message_id=msg.message_id,
                        reply_token=msg.reply_token,
                        session_id=msg.session_id,
                        extra_data=msg.extra_data,
                        timestamp=msg.timestamp
                    )
                    target.add(new_msg)
            
            await target.commit()
            print(f"✅ Migrated {len(messages)} chat messages")
        
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await sqlite_engine.dispose()
        await pg_engine.dispose()

async def main():
    """Main migration process"""
    print("🚀 PostgreSQL Migration Tool")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("DATABASE_URL"):
        print("\n❌ Please set DATABASE_URL environment variable")
        print("Example:")
        print("export DATABASE_URL='postgresql://user:pass@host:5432/dbname?sslmode=require'")
        return
    
    # Step 1: Create tables
    print("\n📦 Step 1: Creating PostgreSQL tables")
    success = await create_postgresql_tables()
    
    if not success:
        print("\n❌ Failed to create tables. Aborting migration.")
        return
    
    # Ask user if they want to migrate data
    print("\n" + "=" * 50)
    response = input("Do you want to migrate data from SQLite? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\n📤 Step 2: Migrating data")
        await migrate_data()
    else:
        print("\n✅ Tables created. You can migrate data later.")
    
    print("\n✨ Done!")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
