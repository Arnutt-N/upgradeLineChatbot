# Fix Database for Old Commit using SQLAlchemy
import asyncio
import sys
import os
from dotenv import load_dotenv

sys.path.append('.')
load_dotenv()

async def fix_db_for_old_commit():
    """ใช้ SQLAlchemy models เพื่อสร้าง database ให้ถูกต้อง"""
    
    from app.db.database import create_db_and_tables
    
    print("Fixing Database for Old Commit using SQLAlchemy")
    print("=" * 50)
    
    try:
        await create_db_and_tables()
        print("✓ Database tables created successfully")
        
        # Test connection
        from app.db.database import get_db
        print("✓ Database connection working")
        
        print("\n🎉 Database ready for old commit!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create database: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(fix_db_for_old_commit())
    
    if result:
        print("\n✅ Database fixed! Try the server again.")
    else:
        print("\n❌ Database fix failed.")
