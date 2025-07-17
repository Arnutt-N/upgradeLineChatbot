# Check for duplicate messages in chat history
import asyncio
import sys
from collections import Counter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, func

sys.path.append('.')
from app.db.models import ChatHistory

async def check_duplicates():
    """Check for duplicate messages in chat history"""
    engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db", echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get all messages for analysis
        result = await session.execute(
            select(ChatHistory).order_by(ChatHistory.timestamp.desc())
        )
        all_messages = result.scalars().all()
        
        print(f"\n📊 Total messages: {len(all_messages)}")
        
        # Check for exact duplicates
        message_counts = Counter()
        duplicate_pairs = []
        
        for msg in all_messages:
            key = (msg.user_id, msg.message_type, msg.message_content, msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            message_counts[key] += 1
            
        # Find duplicates
        duplicates = {k: v for k, v in message_counts.items() if v > 1}
        
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} duplicate message sets:")
            for (user_id, msg_type, content, timestamp), count in list(duplicates.items())[:5]:
                print(f"\n  Duplicate {count}x:")
                print(f"    User: {user_id[-6:]}")
                print(f"    Type: {msg_type}")
                print(f"    Time: {timestamp}")
                print(f"    Message: {content[:50]}...")
        else:
            print("\n✅ No exact duplicates found")
        
        # Check for messages with very close timestamps
        print("\n🔍 Checking for messages with identical timestamps...")
        timestamp_groups = {}
        
        for msg in all_messages:
            timestamp_key = (msg.user_id, msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
            if timestamp_key not in timestamp_groups:
                timestamp_groups[timestamp_key] = []
            timestamp_groups[timestamp_key].append(msg)
        
        # Find groups with multiple messages
        multi_msg_groups = {k: v for k, v in timestamp_groups.items() if len(v) > 1}
        
        if multi_msg_groups:
            print(f"\n⚠️  Found {len(multi_msg_groups)} timestamp groups with multiple messages:")
            for (user_id, timestamp), messages in list(multi_msg_groups.items())[:3]:
                print(f"\n  {len(messages)} messages at {timestamp} for user {user_id[-6:]}:")
                for msg in messages:
                    print(f"    [{msg.message_type}] {msg.message_content[:40]}...")
        else:
            print("\n✅ No timestamp collisions found")

if __name__ == "__main__":
    print("Checking for Duplicate Messages...")
    print("=" * 50)
    asyncio.run(check_duplicates())
