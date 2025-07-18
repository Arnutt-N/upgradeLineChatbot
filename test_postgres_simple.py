# Test PostgreSQL Connection (Simple Version)
import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

async def test_connection():
    """Test PostgreSQL connection and show database info"""
    # Load environment variables
    load_dotenv()
    
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("ERROR: DATABASE_URL not found in .env file")
        print("TIP: Please set DATABASE_URL in your .env file")
        return
    
    # Convert to asyncpg URL if needed
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print(f"Connecting to PostgreSQL...")
    print(f"Host: {DATABASE_URL.split('@')[1].split('/')[0]}")
    
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    try:
        # Test basic connection
        async with engine.connect() as conn:
            # Get PostgreSQL version
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"SUCCESS: Connected successfully!")
            print(f"PostgreSQL Version: {version.split(',')[0]}")
            
            # Get database size
            result = await conn.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """))
            db_size = result.scalar()
            print(f"Database Size: {db_size}")
            
            # List tables
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\nTables found ({len(tables)}):")
                for table in tables:
                    # Get row count for each table
                    count_result = await conn.execute(
                        text(f"SELECT COUNT(*) FROM {table}")
                    )
                    count = count_result.scalar()
                    print(f"  - {table}: {count} rows")
            else:
                print("\nWARNING: No tables found. Run migration script first.")
            
            # Test write permission
            try:
                await conn.execute(text("CREATE TEMP TABLE test_write (id INT)"))
                await conn.execute(text("DROP TABLE test_write"))
                print("\nWrite permissions: OK")
            except Exception as e:
                print(f"\nWrite permissions: Failed - {e}")
                
    except Exception as e:
        print(f"\nERROR: Connection failed!")
        print(f"Error: {e}")
        print("\nCommon issues:")
        print("  1. Check DATABASE_URL format")
        print("  2. Verify password is correct")
        print("  3. Ensure SSL mode is set (?sslmode=require)")
        print("  4. Check if IP is whitelisted (if applicable)")
        
    finally:
        await engine.dispose()
        print("\nConnection closed")

if __name__ == "__main__":
    print("PostgreSQL Connection Test")
    print("=" * 50)
    asyncio.run(test_connection())
