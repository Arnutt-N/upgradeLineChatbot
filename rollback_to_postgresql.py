"""
Script สำหรับ Rollback และ Migrate ข้อมูลจาก SQLite ไปยัง PostgreSQL
สำหรับใช้กับ Render + Supabase
"""
import asyncio
import os
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.postgres')  # ใช้ไฟล์ .env.postgres ที่มี DATABASE_URL ของ PostgreSQL

# Import models
from app.db.models import Base, UserStatus, ChatHistory, FriendActivity

async def export_sqlite_data():
    """ส่งออกข้อมูลจาก SQLite เป็น JSON"""
    print("📤 กำลังส่งออกข้อมูลจาก SQLite...")
    
    # สร้าง engine สำหรับ SQLite
    sqlite_engine = create_async_engine("sqlite+aiosqlite:///./chatbot.db")
    async_session = sessionmaker(sqlite_engine, class_=AsyncSession, expire_on_commit=False)
    
    data = {
        "user_status": [],
        "chat_history": [],
        "friend_activity": [],
        "export_date": datetime.now().isoformat()
    }
    
    async with async_session() as session:
        # Export UserStatus
        print("  - กำลังส่งออก UserStatus...")
        result = await session.execute(select(UserStatus))
        users = result.scalars().all()
        for user in users:
            data["user_status"].append({
                "user_id": user.user_id,
                "display_name": user.display_name,
                "picture_url": user.picture_url,
                "is_in_live_chat": user.is_in_live_chat,
                "chat_mode": user.chat_mode,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            })
        print(f"    ✓ ส่งออก {len(users)} users")
        
        # Export ChatHistory (ทั้งหมดหรือจำกัดจำนวน)
        print("  - กำลังส่งออก ChatHistory...")
        result = await session.execute(
            select(ChatHistory).order_by(ChatHistory.timestamp.desc())
        )
        chats = result.scalars().all()
        for chat in chats:
            data["chat_history"].append({
                "id": chat.id,
                "user_id": chat.user_id,
                "message_type": chat.message_type,
                "message_content": chat.message_content,
                "admin_user_id": chat.admin_user_id,
                "is_read": chat.is_read,
                "message_id": chat.message_id,
                "reply_token": chat.reply_token,
                "session_id": chat.session_id,
                "extra_data": chat.extra_data,
                "timestamp": chat.timestamp.isoformat() if chat.timestamp else None
            })
        print(f"    ✓ ส่งออก {len(chats)} messages")
        
        # Export FriendActivity
        print("  - กำลังส่งออก FriendActivity...")
        result = await session.execute(select(FriendActivity))
        activities = result.scalars().all()
        for activity in activities:
            data["friend_activity"].append({
                "id": activity.id,
                "user_id": activity.user_id,
                "activity_type": activity.activity_type,
                "user_profile": activity.user_profile,
                "source": activity.source,
                "event_data": activity.event_data,
                "timestamp": activity.timestamp.isoformat() if activity.timestamp else None
            })
        print(f"    ✓ ส่งออก {len(activities)} activities")
    
    # บันทึกเป็นไฟล์
    filename = f"sqlite_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ ส่งออกข้อมูลเสร็จสิ้น: {filename}")
    await sqlite_engine.dispose()
    return filename, data

async def setup_postgresql():
    """สร้างตารางใน PostgreSQL"""
    print("\n🔧 กำลังตั้งค่า PostgreSQL...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise Exception("❌ ไม่พบ DATABASE_URL ใน environment variables")
    
    # แปลง URL สำหรับ asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"  - เชื่อมต่อกับ: {DATABASE_URL.split('@')[1]}")  # แสดงเฉพาะส่วน host
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # สร้างตารางทั้งหมด
        async with engine.begin() as conn:
            print("  - กำลังสร้างตาราง...")
            await conn.run_sync(Base.metadata.create_all)
            print("  ✓ สร้างตารางเสร็จสิ้น")
            
            # ตรวจสอบตารางที่สร้าง
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            print(f"  ✓ ตารางที่สร้าง: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")
        raise
    finally:
        await engine.dispose()
    
    return engine

async def import_to_postgresql(filename: str, data: dict):
    """นำเข้าข้อมูลไปยัง PostgreSQL"""
    print(f"\n📥 กำลังนำเข้าข้อมูลไปยัง PostgreSQL...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Import UserStatus
            print("  - กำลังนำเข้า UserStatus...")
            imported_users = 0
            for user_data in data["user_status"]:
                # ตรวจสอบว่ามี user นี้แล้วหรือไม่
                existing = await session.get(UserStatus, user_data["user_id"])
                if not existing:
                    # แปลงวันที่
                    if user_data.get("created_at"):
                        user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                    if user_data.get("updated_at"):
                        user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])
                    
                    user = UserStatus(**user_data)
                    session.add(user)
                    imported_users += 1
            await session.commit()
            print(f"    ✓ นำเข้า {imported_users} users")
            
            # Import ChatHistory
            print("  - กำลังนำเข้า ChatHistory...")
            imported_chats = 0
            for chat_data in data["chat_history"]:
                # ตรวจสอบว่ามี chat นี้แล้วหรือไม่
                existing = await session.get(ChatHistory, chat_data["id"])
                if not existing:
                    # แปลงวันที่
                    if chat_data.get("timestamp"):
                        chat_data["timestamp"] = datetime.fromisoformat(chat_data["timestamp"])
                    
                    chat = ChatHistory(**chat_data)
                    session.add(chat)
                    imported_chats += 1
                    
                    # Commit ทุก 100 records
                    if imported_chats % 100 == 0:
                        await session.commit()
                        print(f"    ... นำเข้าแล้ว {imported_chats} messages")
            
            await session.commit()
            print(f"    ✓ นำเข้า {imported_chats} messages")
            
            # Import FriendActivity
            print("  - กำลังนำเข้า FriendActivity...")
            imported_activities = 0
            for activity_data in data["friend_activity"]:
                existing = await session.get(FriendActivity, activity_data["id"])
                if not existing:
                    if activity_data.get("timestamp"):
                        activity_data["timestamp"] = datetime.fromisoformat(activity_data["timestamp"])
                    
                    activity = FriendActivity(**activity_data)
                    session.add(activity)
                    imported_activities += 1
            
            await session.commit()
            print(f"    ✓ นำเข้า {imported_activities} activities")
            
            print("✅ นำเข้าข้อมูลเสร็จสิ้น!")
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดในการนำเข้า: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()

async def verify_migration():
    """ตรวจสอบผลการ migration"""
    print("\n🔍 กำลังตรวจสอบผลการ migration...")
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    async with engine.connect() as conn:
        # นับจำนวน records ในแต่ละตาราง
        tables = ['user_status', 'chat_history', 'friend_activity']
        for table in tables:
            result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.scalar()
            print(f"  - {table}: {count} records")
        
        # ตรวจสอบข้อมูลล่าสุด
        result = await conn.execute(text("""
            SELECT user_id, message_type, message_content, timestamp 
            FROM chat_history 
            ORDER BY timestamp DESC 
            LIMIT 5
        """))
        print("\n  📋 ข้อความล่าสุด 5 รายการ:")
        for row in result:
            print(f"    - [{row[3]}] {row[0]} ({row[1]}): {row[2][:50]}...")
    
    await engine.dispose()
    print("\n✅ การตรวจสอบเสร็จสิ้น")

async def main():
    """ฟังก์ชันหลักสำหรับ rollback"""
    print("🚀 เริ่มต้นกระบวนการ Rollback to PostgreSQL")
    print("=" * 60)
    
    try:
        # 1. Export ข้อมูลจาก SQLite
        filename, data = await export_sqlite_data()
        
        # 2. Setup PostgreSQL
        await setup_postgresql()
        
        # 3. Import ข้อมูลไป PostgreSQL
        await import_to_postgresql(filename, data)
        
        # 4. Verify migration
        await verify_migration()
        
        print("\n" + "=" * 60)
        print("✅ Rollback เสร็จสมบูรณ์!")
        print("\n📝 ขั้นตอนต่อไป:")
        print("1. อัพเดท .env ใน Render ให้ใช้ DATABASE_URL ของ PostgreSQL")
        print("2. ตั้งค่า DB_TYPE=postgresql")
        print("3. Deploy ใหม่บน Render")
        
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
