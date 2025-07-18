"""
ทดสอบการเชื่อมต่อ PostgreSQL (Supabase)
"""
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

# Load PostgreSQL environment
load_dotenv('.env.postgres')

async def test_connection():
    """ทดสอบการเชื่อมต่อกับ PostgreSQL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ ไม่พบ DATABASE_URL ใน .env.postgres")
        print("กรุณาตั้งค่า DATABASE_URL ใน .env.postgres")
        return
    
    # ซ่อน password ในการแสดงผล
    display_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"🔄 กำลังเชื่อมต่อกับ: {display_url}")
    
    # แปลงสำหรับ asyncpg
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    try:
        async with engine.connect() as conn:
            # ทดสอบ query พื้นฐาน
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"\n✅ เชื่อมต่อสำเร็จ!")
            print(f"📊 PostgreSQL Version: {version}")
            
            # ตรวจสอบตารางที่มีอยู่
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\n📦 ตารางที่มีอยู่: {len(tables)} ตาราง")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("\n⚠️  ยังไม่มีตารางใดๆ ในฐานข้อมูล")
            
            # ทดสอบสร้างตารางทดลอง
            print("\n🧪 ทดสอบสร้างตารางทดลอง...")
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # ใส่ข้อมูลทดสอบ
            await conn.execute(text("""
                INSERT INTO test_connection (message) 
                VALUES ('ทดสอบการเชื่อมต่อสำเร็จ! 🎉')
            """))
            
            # อ่านข้อมูลกลับมา
            result = await conn.execute(text("""
                SELECT message, created_at 
                FROM test_connection 
                ORDER BY id DESC 
                LIMIT 1
            """))
            row = result.first()
            if row:
                print(f"✅ ข้อมูลทดสอบ: {row[0]} (เวลา: {row[1]})")
            
            # ลบตารางทดสอบ
            await conn.execute(text("DROP TABLE test_connection"))
            print("🧹 ลบตารางทดสอบเรียบร้อย")
            
            await conn.commit()
            
    except Exception as e:
        print(f"\n❌ เกิดข้อผิดพลาด: {e}")
        print("\n💡 ตรวจสอบ:")
        print("1. DATABASE_URL ถูกต้องหรือไม่")
        print("2. Password ถูกต้องหรือไม่") 
        print("3. Network/Firewall อนุญาตการเชื่อมต่อหรือไม่")
        print("4. Supabase project ยังทำงานอยู่หรือไม่")
        
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("🚀 ทดสอบการเชื่อมต่อ PostgreSQL (Supabase)")
    print("=" * 50)
    asyncio.run(test_connection())
