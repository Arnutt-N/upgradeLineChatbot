# Simple Gemini Test Script
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_basic_gemini():
    """Test basic Gemini functionality"""
    try:
        print("=" * 50)
        print("Testing Basic Gemini Integration")
        print("=" * 50)
        
        # Test service availability
        from app.services.gemini_service import gemini_service, check_gemini_availability
        
        print("\n1. Testing availability...")
        is_available = await check_gemini_availability()
        print(f"   Gemini available: {is_available}")
        
        if not is_available:
            print("   Error: Gemini not available")
            return False
        
        # Test basic text generation
        print("\n2. Testing basic generation...")
        test_message = "Hello, how are you?"
        
        result = await gemini_service.generate_response(
            user_message=test_message,
            user_id="test_user",
            use_session=True
        )
        
        print(f"   Input: {test_message}")
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Response: {result['response'][:100]}...")
        else:
            print(f"   Error: {result.get('error')}")
        
        # Test model info
        print("\n3. Testing model info...")
        model_info = gemini_service.get_model_info()
        print(f"   Model: {model_info['model']}")
        print(f"   Available: {model_info['available']}")
        print(f"   API Type: {model_info['api_type']}")
        
        print("\n" + "=" * 50)
        print("SUCCESS: Basic Gemini test completed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Simple Gemini Test...")
    success = asyncio.run(test_basic_gemini())
    
    if success:
        print("\nTest PASSED! Gemini integration working.")
    else:
        print("\nTest FAILED. Check configuration.")
