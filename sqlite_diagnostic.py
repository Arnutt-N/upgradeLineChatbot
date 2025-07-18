# sqlite_diagnostic.py
"""
SQLite Diagnostic and Deploy Preparation Script
"""
import asyncio
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

def check_sqlite_database():
    """Check existing SQLite database"""
    db_path = "chatbot.db"
    
    print("🔍 Checking SQLite database...")
    
    if os.path.exists(db_path):
        print(f"✅ SQLite database found: {db_path}")
        
        # Check database size
        size = os.path.getsize(db_path)
        print(f"📊 Database size: {size} bytes ({size/1024:.1f} KB)")
        
        # Check tables
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            if tables:
                print(f"📋 Tables found: {len(tables)}")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    print(f"  - {table_name}: {count} records")
            else:
                print("⚠️ No tables found in database")
                
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error reading SQLite database: {e}")
            return False
    else:
        print("⚠️ SQLite database not found")
        print(f"Expected location: {os.path.abspath(db_path)}")
        return False

def update_env_for_sqlite():
    """Update .env.production for SQLite"""
    print("\n🔧 Updating .env.production for SQLite...")
    
    env_content = """# .env.production
# Production Environment Configuration for Render + SQLite

# --- Environment Settings ---
ENVIRONMENT=production
HOST=0.0.0.0
PORT=10000
RELOAD=false
DEBUG=false

# --- Database Configuration (SQLite for deployment) ---
DATABASE_URL=sqlite+aiosqlite:///./chatbot.db
DB_TYPE=sqlite

# --- LINE Bot Configuration ---
LINE_CHANNEL_SECRET=d0de66d23990df6a9294d99353dee371
LINE_CHANNEL_ACCESS_TOKEN=ndG9ts9IbGvaWHWsDCfUKat/uERCOwe6SK1Ey7zWZ6YAFT810ABZ5gjX0L3CZkwfk34oK4bO5EOodnphM/c0PH8Hs1FEb92eOxVRIRv/PMKbBpX2MCNOdJ+1gJqOPkh9aRwbKxygo7xSDGIIVVPw0AdB04t89/1O/w1cDnyilFU=

# --- AI Service Configuration ---
GEMINI_API_KEY=AIzaSyAX3WH2gYTz_U_qOp5v3p1YoDHa1Yr0H7g
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000
GEMINI_ENABLE_SAFETY=false

# --- Optional: Telegram Integration ---
TELEGRAM_BOT_TOKEN=7830232866:AAGdKAkereAkqt0ds58bqHqBp4I-BhM-m0I
TELEGRAM_CHAT_ID=-4945116273

# --- Application Settings ---
NOTIFICATION_QUEUE_SIZE=100
HISTORY_RETENTION_DAYS=90
ANALYTICS_UPDATE_INTERVAL=300

# --- Security ---
SECRET_KEY=auto_generated_by_render

# --- NOTES ---
# Using SQLite for deployment simplicity
# Can migrate to PostgreSQL later if needed
"""
    
    try:
        with open('.env.production', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env.production updated for SQLite")
        return True
    except Exception as e:
        print(f"❌ Error updating .env.production: {e}")
        return False

async def test_sqlite_connection():
    """Test SQLite connection with the production settings"""
    print("\n🧪 Testing SQLite connection...")
    
    load_dotenv('.env.production')
    
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        DATABASE_URL = os.getenv("DATABASE_URL")
        print(f"Database URL: {DATABASE_URL}")
        
        engine = create_async_engine(DATABASE_URL)
        
        async with engine.connect() as conn:
            # Test basic query
            result = await conn.execute(text("SELECT 1"))
            test_result = result.scalar()
            print(f"✅ Basic query test: {test_result}")
            
            # Test table creation
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS test_deploy (
                    id INTEGER PRIMARY KEY,
                    message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Insert test data
            await conn.execute(text("""
                INSERT INTO test_deploy (message) VALUES ('Deploy test successful')
            """))
            
            # Read test data
            result = await conn.execute(text("SELECT message FROM test_deploy ORDER BY id DESC LIMIT 1"))
            message = result.scalar()
            print(f"✅ Test data: {message}")
            
            # Clean up
            await conn.execute(text("DROP TABLE test_deploy"))
            
        await engine.dispose()
        print("✅ SQLite connection test PASSED!")
        return True
        
    except Exception as e:
        print(f"❌ SQLite connection test FAILED: {e}")
        return False

def check_deployment_files():
    """Check all files needed for deployment"""
    print("\n📋 Checking deployment files...")
    
    required_files = [
        'main.py',
        'requirements.txt', 
        '.env.production',
        'migrate_to_production.py',
        'app/main.py',
        'app/db/models.py',
        'app/db/database.py'
    ]
    
    all_good = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING!")
            all_good = False
    
    return all_good

def check_requirements():
    """Check requirements.txt for SQLite compatibility"""
    print("\n📦 Checking requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'sqlalchemy',
            'aiosqlite',
            'line-bot-sdk',
            'google-generativeai'
        ]
        
        missing_packages = []
        for package in required_packages:
            if package.lower() not in content.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ Missing packages: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ All required packages found")
            return True
            
    except FileNotFoundError:
        print("❌ requirements.txt not found!")
        return False

async def full_diagnostic():
    """Run complete diagnostic"""
    print("=" * 60)
    print("🚀 SQLite Deployment Diagnostic")
    print("=" * 60)
    
    results = []
    
    # 1. Check existing database
    print("\n1. Checking existing SQLite database...")
    db_ok = check_sqlite_database()
    results.append(("SQLite Database", db_ok))
    
    # 2. Update environment file
    print("\n2. Updating environment configuration...")
    env_ok = update_env_for_sqlite()
    results.append(("Environment Config", env_ok))
    
    # 3. Test SQLite connection
    print("\n3. Testing SQLite connection...")
    conn_ok = await test_sqlite_connection()
    results.append(("SQLite Connection", conn_ok))
    
    # 4. Check deployment files
    print("\n4. Checking deployment files...")
    files_ok = check_deployment_files()
    results.append(("Deployment Files", files_ok))
    
    # 5. Check requirements
    print("\n5. Checking requirements.txt...")
    req_ok = check_requirements()
    results.append(("Requirements", req_ok))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, status in results:
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name}")
        if not status:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Ready for deployment!")
        print("\nNext steps:")
        print("1. git add . && git commit -m 'Prepare for SQLite deployment'")
        print("2. git push origin main")
        print("3. Deploy to Render with SQLite")
        print("4. Can migrate to PostgreSQL later if needed")
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")
    
    return all_passed

if __name__ == "__main__":
    success = asyncio.run(full_diagnostic())
    if success:
        print("\n✅ Ready to deploy with SQLite!")
    else:
        print("\n❌ Please fix the issues before deploying.")
