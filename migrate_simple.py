#!/usr/bin/env python3
"""
Database Migration Script for Forms Admin System
Phase 2: Database Migration
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
    """Check existing tables"""
    print("Checking existing tables...")
    
    async with async_engine.begin() as conn:
        result = await conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        )
        tables = [row[0] for row in result.fetchall()]
        
        print(f"Existing tables ({len(tables)}):")
        for table in tables:
            print(f"  - {table}")
        
        return tables

async def migrate_database():
    """Migrate database"""
    print("Starting database migration...")
    
    try:
        # Check existing tables
        existing_tables = await check_existing_tables()
        
        # Create new tables
        print("\nCreating new tables...")
        await create_db_and_tables()
        
        # Check tables after migration
        print("\nChecking tables after migration...")
        new_tables = await check_existing_tables()
        
        # Show added tables
        added_tables = set(new_tables) - set(existing_tables)
        if added_tables:
            print(f"\nNew tables added ({len(added_tables)}):")
            for table in sorted(added_tables):
                print(f"  + {table}")
        else:
            print("\nNo new tables were added (already exist)")
        
        print("\nDatabase migration completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nMigration failed: {e}")
        return False

async def main():
    """Main migration function"""
    print("=" * 50)
    print("FORMS ADMIN DATABASE MIGRATION")
    print("=" * 50)
    
    try:
        success = await migrate_database()
        
        if success:
            print("\nMigration Summary:")
            print("  - Database migration: SUCCESS")
            print("  - Forms Admin system is ready!")
        else:
            print("\nMigration failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
    
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
