import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

sys.path.append('.')
from app.db.models import ChatHistory

async def check_similar_messages():
    """Check for messages that might be duplicated with different types"""
    engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get messages from the last 24 hours
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        result = await session.execute(
            select(ChatHistory)
            .where(ChatHistory.timestamp > cutoff_time)
            .order_by(ChatHistory.user_id, ChatHistory.timestamp)
        )
        messages = result.scalars().all()
        
        print(f"Total messages in last 24 hours: {len(messages)}")
        print("\nChecking for potential duplicates (same content within 5 seconds)...")
        print("-" * 80)
        
        # Group by user and check for similar messages
        current_user = None
        prev_messages = []
        duplicates_found = 0
        
        for msg in messages:
            if current_user != msg.user_id:
                current_user = msg.user_id
                prev_messages = []
            
            # Check if this message is similar to recent ones
            for prev_msg in prev_messages:
                time_diff = abs((msg.timestamp - prev_msg.timestamp).total_seconds())
                
                # If same content within 5 seconds
                if (msg.message_content == prev_msg.message_content and 
                    time_diff < 5 and 
                    msg.message_type != prev_msg.message_type):
                    
                    duplicates_found += 1
                    print(f"\nPotential duplicate #{duplicates_found}:")
                    print(f"  User: {msg.user_id[-6:]}")
                    print(f"  Content: {msg.message_content[:60]}...")
                    print(f"  Type 1: {prev_msg.message_type} at {prev_msg.timestamp.strftime('%H:%M:%S')}")
                    print(f"  Type 2: {msg.message_type} at {msg.timestamp.strftime('%H:%M:%S')}")
                    print(f"  Time diff: {time_diff:.1f} seconds")
            
            # Keep only recent messages for comparison (within 10 seconds)
            cutoff = msg.timestamp - timedelta(seconds=10)
            prev_messages = [m for m in prev_messages if m.timestamp > cutoff]
            prev_messages.append(msg)
        
        print(f"\n\nTotal potential duplicates found: {duplicates_found}")
        
        # Check message type distribution
        print("\n\nMessage type distribution:")
        type_counts = await session.execute(
            select(ChatHistory.message_type, func.count(ChatHistory.id))
            .where(ChatHistory.timestamp > cutoff_time)
            .group_by(ChatHistory.message_type)
        )
        for msg_type, count in type_counts:
            print(f"  {msg_type}: {count}")

if __name__ == "__main__":
    print("Checking for Similar Messages...")
    print("=" * 50)
    asyncio.run(check_similar_messages())
