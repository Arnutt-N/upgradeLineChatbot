# คู่มือการตั้งค่า PostgreSQL Supabase กับ Render

## 1. การตั้งค่า Supabase (Database)

### 1.1 สร้างโปรเจคใน Supabase
1. ไปที่ https://supabase.com และ Sign up/Login
2. คลิก "New project"
3. ตั้งค่าโปรเจค:
   - **Name**: `linechatbot-db` (หรือชื่อที่ต้องการ)
   - **Database Password**: สร้าง password ที่แข็งแรง (จดไว้!)
   - **Region**: เลือก `Singapore` (ใกล้ไทย)
   - **Pricing Plan**: Free tier (ถ้าเพิ่งเริ่ม)

### 1.2 รับ Connection String
1. ไปที่ Settings > Database
2. ในส่วน Connection string เลือก "URI"
3. Copy connection string ที่มีรูปแบบ:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
   ```

### 1.3 ตั้งค่า SSL Mode
เพิ่ม `?sslmode=require` ต่อท้าย connection string:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
```

## 2. ปรับปรุงโปรเจคสำหรับ PostgreSQL

### 2.1 สร้างไฟล์ .env สำหรับ PostgreSQL
```bash
# .env.postgres
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE=postgresql

# Keep existing settings
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
GEMINI_API_KEY=your_gemini_api_key
# ... other settings
```

### 2.2 Update database.py
```python
# app/db/database.py
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.db.models import Base

# ตรวจสอบ DB type
DB_TYPE = os.getenv("DB_TYPE", "sqlite")
DATABASE_URL = os.getenv("DATABASE_URL")

if DB_TYPE == "postgresql" and DATABASE_URL:
    # PostgreSQL with asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        poolclass=NullPool,  # Recommended for serverless
        connect_args={
            "server_settings": {"jit": "off"},
            "command_timeout": 60,
        }
    )
else:
    # SQLite fallback
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"
    engine = create_async_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

### 2.3 Create Migration Script
```python
# migrate_to_postgresql.py
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.models import Base

async def migrate_to_postgresql():
    """Create all tables in PostgreSQL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        return
    
    # Convert to asyncpg URL
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"🔄 Connecting to PostgreSQL...")
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.begin() as conn:
            print("📦 Creating tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("✅ All tables created successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(migrate_to_postgresql())
```

## 3. การตั้งค่า Render

### 3.1 เตรียม Repository
1. Push code ล่าสุดไปที่ GitHub
2. ตรวจสอบว่ามีไฟล์ `requirements.txt` และ `render.yaml`

### 3.2 สร้าง render.yaml
```yaml
# render.yaml
services:
  - type: web
    name: line-chatbot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: DB_TYPE
        value: postgresql
      - key: LINE_CHANNEL_SECRET
        sync: false
      - key: LINE_CHANNEL_ACCESS_TOKEN
        sync: false
      - key: GEMINI_API_KEY
        sync: false
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: TELEGRAM_CHAT_ID
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
```

### 3.3 Deploy บน Render
1. ไปที่ https://render.com และ login
2. คลิก "New +" > "Web Service"
3. เชื่อมต่อ GitHub repository
4. เลือก repository และ branch
5. ตั้งค่า:
   - **Name**: `line-chatbot`
   - **Region**: Singapore
   - **Branch**: `main` หรือ `fix/admin-realtime-chat`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3.4 ตั้งค่า Environment Variables
ใน Render Dashboard > Environment:
```
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE=postgresql
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
GEMINI_API_KEY=your_gemini_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
ENVIRONMENT=production
```

## 4. การ Migrate ข้อมูลจาก SQLite

### 4.1 Export ข้อมูลจาก SQLite
```python
# export_sqlite_data.py
import asyncio
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.db.models import UserStatus, ChatHistory, FriendActivity

async def export_data():
    # SQLite engine
    engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    data = {
        "user_status": [],
        "chat_history": [],
        "friend_activity": []
    }
    
    async with async_session() as session:
        # Export UserStatus
        result = await session.execute(select(UserStatus))
        for user in result.scalars().all():
            data["user_status"].append({
                "user_id": user.user_id,
                "display_name": user.display_name,
                "picture_url": user.picture_url,
                "is_in_live_chat": user.is_in_live_chat,
                "chat_mode": user.chat_mode
            })
        
        # Export ChatHistory (limit to recent)
        result = await session.execute(
            select(ChatHistory).order_by(ChatHistory.timestamp.desc()).limit(1000)
        )
        for chat in result.scalars().all():
            data["chat_history"].append({
                "id": chat.id,
                "user_id": chat.user_id,
                "message_type": chat.message_type,
                "message_content": chat.message_content,
                "timestamp": chat.timestamp.isoformat()
            })
    
    with open("backup_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Exported {len(data['user_status'])} users, {len(data['chat_history'])} messages")

if __name__ == "__main__":
    asyncio.run(export_data())
```

### 4.2 Import ข้อมูลไป PostgreSQL
```python
# import_to_postgresql.py
import asyncio
import json
import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.db.models import UserStatus, ChatHistory

async def import_data():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    with open("backup_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    async with async_session() as session:
        # Import UserStatus
        for user_data in data["user_status"]:
            user = UserStatus(**user_data)
            session.add(user)
        
        # Import ChatHistory
        for chat_data in data["chat_history"]:
            chat_data["timestamp"] = datetime.fromisoformat(chat_data["timestamp"])
            chat = ChatHistory(**chat_data)
            session.add(chat)
        
        await session.commit()
        print("✅ Data imported successfully!")

if __name__ == "__main__":
    asyncio.run(import_data())
```

## 5. ตรวจสอบและ Troubleshooting

### 5.1 ทดสอบการเชื่อมต่อ
```python
# test_postgresql_connection.py
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL: {version}")
            
            # Test tables
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print(f"📦 Tables: {tables}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
```

### 5.2 ปัญหาที่อาจพบ

1. **Connection refused**
   - ตรวจสอบ connection string
   - ตรวจสอบว่าใส่ password ถูกต้อง
   - ตรวจสอบ SSL mode

2. **Tables not found**
   - รัน migration script
   - ตรวจสอบว่า models ถูก import

3. **Performance issues**
   - เพิ่ม indexes ที่จำเป็น
   - ใช้ connection pooling
   - พิจารณา upgrade Supabase plan

## 6. Best Practices

1. **Security**
   - ใช้ environment variables เสมอ
   - ไม่ commit secrets ลง git
   - ใช้ SSL connections

2. **Performance**
   - สร้าง indexes สำหรับ queries ที่ใช้บ่อย
   - ใช้ pagination สำหรับข้อมูลจำนวนมาก
   - Monitor database performance

3. **Backup**
   - ตั้ง automated backups ใน Supabase
   - Export ข้อมูลสำคัญเป็นระยะ

---
สร้างเมื่อ: ${new Date().toISOString()}
