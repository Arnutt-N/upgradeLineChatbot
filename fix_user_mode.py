# Fix User Mode to Auto
import asyncio
from app.db.database import get_db
from app.db.crud import get_or_create_user_status

async def fix_user_mode():
    """Fix user mode to enable automatic bot responses"""
    print("Fixing user mode to enable bot responses...")
    
    async for db in get_db():
        try:
            user_id = "U693cb72c4dff8525756775d5fce45296"  # From logs
            
            # Get user status
            user_status = await get_or_create_user_status(
                db, user_id, "Arnutt Topp", None
            )
            
            print(f"Current status:")
            print(f"  - Is in live chat: {user_status.is_in_live_chat}")
            print(f"  - Chat mode: {user_status.chat_mode}")
            
            # Set to auto mode for bot responses
            user_status.chat_mode = 'auto'
            await db.commit()
            
            print(f"Updated status:")
            print(f"  - Is in live chat: {user_status.is_in_live_chat}")
            print(f"  - Chat mode: {user_status.chat_mode}")
            print("User is now set to auto mode - bot will respond!")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(fix_user_mode())