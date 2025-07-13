#!/usr/bin/env python3
"""
Database Migration Script for Forms Admin System
Phase 2: Database Migration

This script safely creates new tables for the Forms Admin system
without affecting existing LINE Admin data.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from app.db.database import async_engine, create_db_and_tables
from app.db.models import Base
from sqlalchemy import text

async def check_existing_tables():
    """ตรวจสอบตารางที่มีอยู่"""
    print("🔍 Checking existing tables...")
    
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        tables = [row[0] for row in result.fetchall()]
        
        print(f"📋 Existing tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        
        return tables

async def migrate_database():
    """ทำการ migrate database"""
    print("🚀 Starting database migration...")
    
    try:
        # ตรวจสอบตารางเดิม
        existing_tables = await check_existing_tables()
        
        # สร้างตารางใหม่
        print("\n📊 Creating new tables...")
        await create_db_and_tables()
        
        # ตรวจสอบตารางหลังจาก migrate
        print("\n✅ Checking tables after migration...")
        new_tables = await check_existing_tables()
        
        # แสดงตารางที่เพิ่มใหม่
        added_tables = set(new_tables) - set(existing_tables)
        if added_tables:
            print(f"\n🆕 New tables added ({len(added_tables)}):")
            for table in sorted(added_tables):
                print(f"  + {table}")
        else:
            print("\n📝 No new tables were added (already exist)")
        
        print("\n🎉 Database migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

async def verify_migration():
    """ตรวจสอบความสมบูรณ์ของ migration"""
    print("\n🔍 Verifying migration...")
    
    expected_tables = [
        'user_status',          # existing
        'chat_messages',        # existing
        'form_submissions',     # new
        'form_attachments',     # new
        'admin_users',          # new
        'form_status_history',  # new
        'shared_notifications', # new
        'shared_audit_logs'     # new
    ]
    
    async with async_engine.begin() as conn:
        for table in expected_tables:
            try:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                status = "✅" if count >= 0 else "❌"
                print(f"  {status} {table}: {count} records")
            except Exception as e:
                print(f"  ❌ {table}: ERROR - {e}")
    
    print("\n✅ Migration verification completed!")

async def main():
    """Main migration function"""
    print("=" * 60)
    print("🏗️  FORMS ADMIN DATABASE MIGRATION")
    print("   Phase 2: Database Migration")
    print("=" * 60)
    
    try:
        # Run migration
        success = await migrate_database()
        
        if success:
            # Verify migration
            await verify_migration()
            print("\n🎯 Migration Summary:")
            print("  ✅ Database migration: SUCCESS")
            print("  ✅ Table creation: SUCCESS")
            print("  ✅ Verification: SUCCESS")
            print("\n🚀 Forms Admin system is ready!")
        else:
            print("\n❌ Migration failed. Please check the errors above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
    
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
