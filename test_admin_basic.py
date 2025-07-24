# Test Admin Panel Functions
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append('.')
load_dotenv()

async def test_admin_panel_functions():
    """Test admin panel functions"""
    
    print("Testing Admin Panel Functions")
    print("=" * 40)
    
    # Test 1: Database connection and models
    try:
        from app.db.database import get_db, create_db_and_tables
        from app.db.crud_enhanced import (
            save_chat_to_history, 
            get_all_chat_history_by_user,
            get_users_with_history,
            get_latest_chat_in_history
        )
        from app.db.models import Base
        
        print("Successfully imported database modules")
        
        # Test database connection
        await create_db_and_tables()
        print("Database connection successful")
        
    except Exception as e:
        print(f"Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_admin_panel_functions())
    
    if result:
        print("\nAdmin Panel basic test passed!")
    else:
        print("\nSome tests failed - check the errors above")
