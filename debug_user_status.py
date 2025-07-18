# Debug User Status
import asyncio
from app.db.database import get_db
from app.db.crud import get_or_create_user_status
from sqlalchemy.ext.asyncio import AsyncSession

async def debug_user_status():
    """Debug user status to understand chat mode"""
    print("Debugging user status...")
    
    # Get database session
    async for db in get_db():
        try:
            user_id = "U693cb72c4dff8525756775d5fce45296"  # From logs
            
            # Get user status
            user_status = await get_or_create_user_status(
                db, user_id, "Test User", None
            )
            
            print(f"User ID: {user_id}")
            print(f"Display Name: {user_status.display_name}")
            print(f"Is in live chat: {user_status.is_in_live_chat}")
            print(f"Chat mode: {user_status.chat_mode}")
            print(f"Created at: {user_status.created_at}")
            print(f"Updated at: {user_status.updated_at}")
            
            # Check if we need to reset the user to bot mode
            if user_status.is_in_live_chat and user_status.chat_mode != 'auto':
                print("\n🔧 User is in live chat but not in auto mode")
                print("This might be why the bot isn't responding")
                
                # Set to auto mode for testing
                user_status.chat_mode = 'auto'
                await db.commit()
                print("✅ Set chat mode to 'auto' for testing")
            
            elif not user_status.is_in_live_chat:
                print("\n🔧 User is NOT in live chat - bot mode should be working")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(debug_user_status())