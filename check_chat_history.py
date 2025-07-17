# Script to check chat history in database
import asyncio
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

# Add app directory to path
sys.path.append('.')

from app.db.models import ChatHistory, UserStatus

async def check_chat_history():
    """Check chat history records in database"""
    # Create async engine
    engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Count total messages
        total_count = await session.scalar(select(func.count(ChatHistory.id)))
        print(f"\n📊 Total messages in chat_history: {total_count}")
        
        # Count by message type
        print("\n📈 Messages by type:")
        type_counts = await session.execute(
            select(ChatHistory.message_type, func.count(ChatHistory.id))
            .group_by(ChatHistory.message_type)
        )
        for msg_type, count in type_counts:
            print(f"  - {msg_type}: {count}")
        
        # Get recent messages
        print("\n📝 Recent 10 messages:")
        result = await session.execute(
            select(ChatHistory)
            .order_by(ChatHistory.timestamp.desc())
            .limit(10)
        )
        messages = result.scalars().all()
        
        for msg in messages:
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            content = msg.message_content[:50] + "..." if len(msg.message_content) > 50 else msg.message_content
            print(f"  [{timestamp}] {msg.message_type} - {msg.user_id}: {content}")
        
        # Check users with messages
        print("\n👥 Users with messages:")
        user_messages = await session.execute(
            select(ChatHistory.user_id, func.count(ChatHistory.id))
            .group_by(ChatHistory.user_id)
            .order_by(func.count(ChatHistory.id).desc())
            .limit(5)
        )
        for user_id, msg_count in user_messages:
            # Get user info
            user = await session.get(UserStatus, user_id)
            display_name = user.display_name if user else f"Unknown ({user_id[-6:]})"
            print(f"  - {display_name}: {msg_count} messages")

if __name__ == "__main__":
    print("Checking Chat History Database...")
    print("=" * 50)
    asyncio.run(check_chat_history())
    print("\nCheck completed!")
