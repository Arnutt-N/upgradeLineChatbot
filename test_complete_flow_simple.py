# Test Complete Flow Simple
import asyncio
from app.services.gemini_service import gemini_service

async def test_complete_flow_simple():
    """Test the complete flow with current configuration"""
    print("Testing complete flow with current configuration...")
    
    # Test 1: Check model and safety settings
    model_info = gemini_service.get_model_info()
    print(f"Model info:")
    print(f"  Available: {model_info['available']}")
    print(f"  Model: {model_info['model']}")
    print(f"  Safety enabled: {model_info['safety_enabled']}")
    
    # Test 2: Test basic response
    try:
        result = await gemini_service.generate_response(
            user_message="สวัสดีครับ",
            user_id="test_user",
            use_session=True
        )
        
        print(f"\nBasic response test:")
        print(f"  Success: {result['success']}")
        print(f"  Response length: {len(result.get('response', ''))}")
        print(f"  Model used: {result.get('model', 'Not specified')}")
        
        if result['success']:
            response_text = result['response']
            
            # Check for fallback messages
            fallback_indicators = [
                "ขออภัย ไม่สามารถประมวลผลคำขอได้",
                "ขออภัย เกิดข้อผิดพลาดในระบบ AI",
                "ขออภัย ไม่สามารถตอบคำถามนี้ได้ เนื่องจากระบบความปลอดภัย"
            ]
            
            is_fallback = any(indicator in response_text for indicator in fallback_indicators)
            print(f"  Is fallback message: {is_fallback}")
            
            if not is_fallback:
                print("  RESULT: SUCCESS - Real AI response!")
                return True
            else:
                print("  RESULT: FAILED - Still fallback message")
                return False
        else:
            print("  RESULT: FAILED - Response generation failed")
            return False
            
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_complete_flow_simple())
    
    if result:
        print("\nBot should work correctly now!")
    else:
        print("\nBot may still have issues.")