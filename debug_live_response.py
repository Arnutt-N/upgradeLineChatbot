# Debug Live Response Generation
import asyncio
from app.services.gemini_service import gemini_service
from app.db.database import get_db

async def debug_live_response():
    """Debug the actual response generation process"""
    print("Debugging live response generation...")
    
    # Get database session
    async for db in get_db():
        try:
            user_id = "U693cb72c4dff8525756775d5fce45296"
            test_message = "สวัสดีครับ"
            
            # Mock user profile
            user_profile = {
                "user_id": user_id,
                "display_name": "Arnutt Topp",
                "picture_url": "https://example.com/avatar.jpg"
            }
            
            print(f"Testing generate_smart_reply with:")
            print(f"  User message: {test_message}")
            print(f"  User ID: {user_id}")
            
            # Test the generate_smart_reply function directly
            result = await gemini_service.generate_smart_reply(
                user_message=test_message,
                user_profile=user_profile,
                db=db
            )
            
            print(f"\nResult:")
            print(f"  Success: {result['success']}")
            print(f"  Response length: {len(result.get('response', ''))}")
            print(f"  Model: {result.get('model', 'Not specified')}")
            print(f"  Error: {result.get('error', 'None')}")
            
            if result['success']:
                response_text = result['response']
                print(f"  Response content: {response_text[:200]}...")
                
                # Check if it's a fallback message
                fallback_messages = [
                    "ขออภัย ไม่สามารถประมวลผลคำขอได้ในขณะนี้",
                    "ขออภัย เกิดข้อผิดพลาดในระบบ AI",
                    "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย"
                ]
                
                is_fallback = any(msg in response_text for msg in fallback_messages)
                print(f"  Is fallback message: {is_fallback}")
                
                if not is_fallback:
                    print("  ✅ SUCCESS: Real AI response generated!")
                else:
                    print("  ❌ PROBLEM: Still getting fallback message")
            else:
                print("  ❌ FAILED: Response generation failed")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await db.close()
            break

if __name__ == "__main__":
    asyncio.run(debug_live_response())