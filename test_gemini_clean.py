# Clean Gemini Test without console encoding issues
import asyncio
from app.services.gemini_service import gemini_service

async def test_gemini_clean():
    """Test Gemini without console encoding issues"""
    print("Testing Gemini service (clean test)...")
    
    # Test 1: Check availability
    is_available = gemini_service.is_available()
    print(f"1. Gemini available: {is_available}")
    
    if not is_available:
        print("   ERROR: Gemini not available")
        return False
    
    # Test 2: Test basic response
    try:
        result = await gemini_service.generate_response(
            user_message="สวัสดีครับ",
            user_id="test_user_123",
            use_session=True
        )
        
        print(f"2. Response success: {result['success']}")
        if result['success']:
            response_text = result['response']
            print(f"   Response length: {len(response_text) if response_text else 0}")
            print(f"   Response has content: {bool(response_text and response_text.strip())}")
            
            # Test encoding
            try:
                encoded = response_text.encode('utf-8')
                decoded = encoded.decode('utf-8')
                print(f"   Encoding test: PASSED")
                return True
            except Exception as e:
                print(f"   Encoding test: FAILED - {e}")
                return False
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"   ERROR: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gemini_clean())
    
    if result:
        print("\n✅ Gemini is working! Bot should respond now.")
    else:
        print("\n❌ Gemini test failed.")