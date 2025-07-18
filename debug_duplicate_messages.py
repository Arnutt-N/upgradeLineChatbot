# Debug Duplicate Messages
import asyncio
from app.db.database import get_db
from app.db.crud_enhanced import get_all_chat_history_by_user
from sqlalchemy import text

async def debug_duplicate_messages():
    """Debug duplicate messages in database"""
    print("Debugging duplicate messages...")
    
    async for db in get_db():
        try:
            user_id = "U693cb72c4dff8525756775d5fce45296"
            
            # Get recent messages from database
            messages = await get_all_chat_history_by_user(db, user_id, limit=20)
            
            print(f"Recent messages for user {user_id}:")
            print("="*60)
            
            bot_responses = []
            for i, msg in enumerate(messages):
                print(f"{i+1}. [{msg.timestamp}] {msg.message_type}: {msg.message_content[:50]}...")
                
                # Track bot responses
                if msg.message_type in ['bot', 'ai_bot']:
                    bot_responses.append({
                        'timestamp': msg.timestamp,
                        'type': msg.message_type,
                        'content': msg.message_content,
                        'id': msg.id
                    })
            
            print("\n" + "="*60)
            print(f"Found {len(bot_responses)} bot responses:")
            
            # Check for duplicates
            duplicate_found = False
            for i, response in enumerate(bot_responses):
                print(f"Bot Response {i+1}: {response['content'][:50]}...")
                
                # Check if this content appears multiple times
                same_content = [r for r in bot_responses if r['content'] == response['content']]
                if len(same_content) > 1:
                    print(f"  ❌ DUPLICATE FOUND! This response appears {len(same_content)} times:")
                    for dup in same_content:
                        print(f"    ID: {dup['id']}, Time: {dup['timestamp']}")
                    duplicate_found = True
            
            if not duplicate_found:
                print("✅ No duplicate bot responses found in database")
            else:
                print("❌ Duplicate bot responses found in database!")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(debug_duplicate_messages())