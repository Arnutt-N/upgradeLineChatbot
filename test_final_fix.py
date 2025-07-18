# Final Test to verify the complete fix
import asyncio
from app.services.gemini_service import gemini_service

async def test_final_fix():
    """Final test to verify the complete fix"""
    print("Final test: Verifying complete fix...")
    
    # Test Thai greeting
    try:
        result = await gemini_service.generate_response(
            user_message="สวัสดีครับ",
            user_id="test_user_123",
            use_session=True
        )
        
        print(f"Thai greeting test:")
        print(f"  Success: {result['success']}")
        if result['success']:
            response_text = result['response']
            print(f"  Response length: {len(response_text) if response_text else 0}")
            print(f"  Has content: {bool(response_text and response_text.strip())}")
            
            # Check if it's not the fallback message
            is_fallback = "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย" in response_text
            print(f"  Is fallback message: {is_fallback}")
            
            if not is_fallback and response_text and response_text.strip():
                print("  RESULT: SUCCESS - Bot generates proper responses!")
                return True
            else:
                print("  RESULT: STILL BLOCKED - Using fallback message")
                return False
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_final_fix())
    
    if result:
        print("\nSUCCESS: Bot should now respond properly!")
    else:
        print("\nFAILED: Bot may still use fallback messages.")