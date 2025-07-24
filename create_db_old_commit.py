# Create Database for Old Commit
import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def create_database_for_old_commit():
    """สร้างฐานข้อมูลให้ตรงกับ old commit"""
    
    database_url = "sqlite+aiosqlite:///./chatbot.db"
    engine = create_async_engine(database_url, echo=False)
    
    print("Creating Database for Old Commit")
    print("=" * 40)
    
    async with engine.begin() as conn:
        # Create tables according to old commit models
        
        # 1. UserStatus table (without id column)
        await conn.execute(text("""
            CREATE TABLE user_status (
                user_id VARCHAR PRIMARY KEY,
                display_name VARCHAR,
                picture_url VARCHAR,
                is_in_live_chat BOOLEAN DEFAULT 0,
                chat_mode VARCHAR DEFAULT 'manual',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ Created user_status table")
        
        # 2. ChatMessage table
        await conn.execute(text("""
            CREATE TABLE chat_messages (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                sender_type VARCHAR,
                message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ Created chat_messages table")
        
        # 3. ChatHistory table (with all required columns)
        await conn.execute(text("""
            CREATE TABLE chat_history (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                message_type VARCHAR NOT NULL,
                message_content TEXT NOT NULL,
                admin_user_id VARCHAR,
                is_read BOOLEAN DEFAULT 0,
                message_id VARCHAR,
                reply_token VARCHAR,
                session_id VARCHAR,
                extra_data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ Created chat_history table")
        
        # 4. FriendActivity table
        await conn.execute(text("""
            CREATE TABLE friend_activity (
                id VARCHAR PRIMARY KEY,
                user_id VARCHAR NOT NULL,
                activity_type VARCHAR NOT NULL,
                user_profile TEXT,
                source VARCHAR DEFAULT 'line_webhook',
                event_data TEXT,
                ip_address VARCHAR,
                user_agent VARCHAR,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✓ Created friend_activity table")
        
        # 5. Create indexes
        await conn.execute(text("CREATE INDEX idx_user_status_user_id ON user_status(user_id)"))
        await conn.execute(text("CREATE INDEX idx_chat_history_user_id ON chat_history(user_id)"))
        await conn.execute(text("CREATE INDEX idx_chat_history_timestamp ON chat_history(timestamp)"))
        print("✓ Created indexes")
        
        # 6. Insert sample data
        print("\nInserting sample data...")
        
        # Sample users
        users = [
            ("U1234567890abcdef1234567890abcdef", "Somchai Jaidee", "https://via.placeholder.com/100", 1, "manual"),
            ("U2345678901bcdef1234567890abcdef1", "Suda Suayngam", "https://via.placeholder.com/100", 0, "auto"),
            ("U3456789012cdef1234567890abcdef12", "Wichai Kengmak", "https://via.placeholder.com/100", 1, "manual")
        ]
        
        for user_id, name, pic, live_chat, mode in users:
            await conn.execute(text("""
                INSERT INTO user_status (user_id, display_name, picture_url, is_in_live_chat, chat_mode)
                VALUES (:user_id, :name, :pic, :live_chat, :mode)
            """), {
                'user_id': user_id,
                'name': name, 
                'pic': pic,
                'live_chat': live_chat,
                'mode': mode
            })
        print("✓ Inserted 3 sample users")
        
        # Sample chat history
        messages = [
            ("msg1", "U1234567890abcdef1234567890abcdef", "user", "Hello, I need help"),
            ("msg2", "U1234567890abcdef1234567890abcdef", "bot", "Hello! How can I help you?"),
            ("msg3", "U1234567890abcdef1234567890abcdef", "user", "I want to apply for leave"),
            ("msg4", "U1234567890abcdef1234567890abcdef", "admin", "Which type of leave?", "admin001"),
            ("msg5", "U1234567890abcdef1234567890abcdef", "user", "Sick leave please"),
        ]
        
        for msg_id, user_id, msg_type, content, admin_id in [m + (None,) if len(m) == 4 else m for m in messages]:
            await conn.execute(text("""
                INSERT INTO chat_history (id, user_id, message_type, message_content, admin_user_id)
                VALUES (:id, :user_id, :msg_type, :content, :admin_id)
            """), {
                'id': msg_id,
                'user_id': user_id,
                'msg_type': msg_type,
                'content': content,
                'admin_id': admin_id
            })
        print("✓ Inserted 5 sample messages")
        
        print(f"\n🎉 Database created successfully!")
        print("Ready for old commit!")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_database_for_old_commit())
