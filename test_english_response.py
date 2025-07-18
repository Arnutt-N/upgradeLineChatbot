# Test English Response
import asyncio
from app.services.gemini_service import gemini_service

async def test_english_response():
    """Test with English to see if it works"""
    print("Testing English response...")
    
    try:
        # Test English
        result = await gemini_service.generate_response(
            user_message="Hello, how are you?",
            user_id="test_user_123",
            use_session=True
        )
        
        print(f"English test:")
        print(f"  Success: {result['success']}")
        if result['success']:
            response_text = result['response']
            print(f"  Response length: {len(response_text) if response_text else 0}")
            print(f"  Has content: {bool(response_text and response_text.strip())}")
            
            # Check if it's not the fallback message
            is_fallback = "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย" in response_text
            print(f"  Is fallback message: {is_fallback}")
            
            if not is_fallback and response_text and response_text.strip():
                print("  RESULT: SUCCESS - English works!")
                
                # Now test Thai
                print("\nTesting Thai response...")
                result2 = await gemini_service.generate_response(
                    user_message="สวัสดี",
                    user_id="test_user_123",
                    use_session=True
                )
                
                print(f"Thai test:")
                print(f"  Success: {result2['success']}")
                if result2['success']:
                    response_text2 = result2['response']
                    print(f"  Response length: {len(response_text2) if response_text2 else 0}")
                    print(f"  Has content: {bool(response_text2 and response_text2.strip())}")
                    
                    is_fallback2 = "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย" in response_text2
                    print(f"  Is fallback message: {is_fallback2}")
                    
                    if not is_fallback2 and response_text2 and response_text2.strip():
                        print("  RESULT: SUCCESS - Thai also works!")
                        return True
                    else:
                        print("  RESULT: Thai still blocked")
                        return False
                
            else:
                print("  RESULT: Even English is blocked")
                return False
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_english_response())
    
    if result:
        print("\nSUCCESS: Bot should work for both languages!")
    else:
        print("\nFAILED: Some issues remain.")