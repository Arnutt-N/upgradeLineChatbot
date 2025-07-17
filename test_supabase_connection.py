# test_supabase_connection.py
"""
Script สำหรับทดสอบการเชื่อมต่อ Supabase PostgreSQL
"""
import asyncio
import os
from dotenv import load_dotenv

# โหลด environment variables
load_dotenv('.env.production')

async def test_connection():
    """ทดสอบการเชื่อมต่อ Supabase"""
    
    # วิธีที่ 1: ใช้ asyncpg โดยตรง
    try:
        import asyncpg
        print("🔍 Testing with asyncpg...")
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ DATABASE_URL not found in .env.production")
            return
        
        # แสดง connection info (ซ่อน password)
        if "@" in DATABASE_URL:
            url_parts = DATABASE_URL.split("@")
            safe_url = url_parts[0].split(":")
            safe_url = f"{safe_url[0]}:****@{url_parts[1]}"
            print(f"📡 Connecting to: {safe_url}")
        
        conn = await asyncpg.connect(DATABASE_URL)
        
        # ทดสอบ query
        version = await conn.fetchval('SELECT version()')
        print(f"✅ Connected successfully!")
        print(f"📊 PostgreSQL version: {version}")
        
        # ดูข้อมูล database
        db_name = await conn.fetchval('SELECT current_database()')
        db_user = await conn.fetchval('SELECT current_user')
        print(f"📁 Database: {db_name}")
        print(f"👤 User: {db_user}")
        
        await conn.close()
        
    except ImportError:
        print("❌ asyncpg not installed. Run: pip install asyncpg")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 ตรวจสอบ:")
        print("1. DATABASE_URL ถูกต้อง")
        print("2. Password ไม่มี [YOUR-PASSWORD]") 
        print("3. มี ?sslmode=require ต่อท้าย")
        print("4. Supabase project ยัง active")

async def test_with_sqlalchemy():
    """ทดสอบด้วย SQLAlchemy (เหมือนที่ app ใช้)"""
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        print("\n🔍 Testing with SQLAlchemy...")
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        engine = create_async_engine(DATABASE_URL, echo=False)
        
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful!")
            
            # List tables
            tables_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            result = await conn.execute(tables_query)
            tables = [row[0] for row in result]
            
            if tables:
                print(f"📋 Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("📋 No tables found (database is empty)")
        
        await engine.dispose()
        
    except ImportError:
        print("❌ SQLAlchemy not installed")
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")

def extract_project_info():
    """แสดงข้อมูล project จาก DATABASE_URL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return
    
    print("\n📊 Connection String Analysis:")
    print("="*50)
    
    # Extract PROJECT-ID
    if ".supabase.co" in DATABASE_URL:
        parts = DATABASE_URL.split("@db.")
        if len(parts) > 1:
            project_id = parts[1].split(".supabase.co")[0]
            print(f"🔑 PROJECT-ID: {project_id}")
    
    # Check SSL mode
    if "sslmode=require" in DATABASE_URL:
        print("🔒 SSL Mode: ✅ Enabled (Good!)")
    else:
        print("⚠️  SSL Mode: ❌ Not set (Add ?sslmode=require)")
    
    # Extract host
    if "@" in DATABASE_URL and ".supabase.co" in DATABASE_URL:
        host_part = DATABASE_URL.split("@")[1].split("/")[0]
        print(f"🌐 Host: {host_part}")

async def main():
    print("🚀 Supabase Connection Test")
    print("="*50)
    
    # แสดงข้อมูลจาก connection string
    extract_project_info()
    
    # ทดสอบการเชื่อมต่อ
    await test_connection()
    await test_with_sqlalchemy()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
