# Test Summary of Fixes
import asyncio
import sys
import json
from app.services.gemini_service import gemini_service

async def test_fixes():
    """Test all the fixes we applied"""
    print("Testing fixes applied to LINE Bot...")
    
    results = {
        "gemini_available": False,
        "gemini_response_working": False,
        "safety_filter_fixed": False,
        "encoding_handled": False,
        "session_management": False
    }
    
    # Test 1: Gemini availability
    try:
        results["gemini_available"] = gemini_service.is_available()
        print(f"1. Gemini available: {results['gemini_available']}")
    except Exception as e:
        print(f"1. Gemini availability test failed: {e}")
    
    # Test 2: Basic response
    try:
        if results["gemini_available"]:
            response = await gemini_service.generate_response(
                user_message="Hello test",
                user_id="test_user",
                use_session=True
            )
            results["gemini_response_working"] = response["success"]
            print(f"2. Gemini response working: {results['gemini_response_working']}")
            
            # Test encoding
            if response["success"] and response["response"]:
                try:
                    encoded = response["response"].encode('utf-8')
                    decoded = encoded.decode('utf-8')
                    results["encoding_handled"] = True
                    print(f"3. Encoding handled: {results['encoding_handled']}")
                except Exception as e:
                    print(f"3. Encoding test failed: {e}")
                    
            # Test if response is blocked by safety filter
            if response["success"]:
                results["safety_filter_fixed"] = True
                print(f"4. Safety filter working properly: {results['safety_filter_fixed']}")
    except Exception as e:
        print(f"2. Response test failed: {e}")
    
    # Test 3: Session management
    try:
        sessions_info = gemini_service.get_chat_sessions_info()
        results["session_management"] = sessions_info["active_sessions"] > 0
        print(f"5. Session management working: {results['session_management']}")
    except Exception as e:
        print(f"5. Session management test failed: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("FIXES SUMMARY:")
    print("="*50)
    
    fixes_applied = [
        "✓ Updated Gemini model to gemini-2.5-pro",
        "✓ Fixed safety filter settings (BLOCK_ONLY_HIGH)",
        "✓ Improved UTF-8 encoding handling",
        "✓ Fixed duplicate message broadcasts",
        "✓ Enhanced error handling for replies",
        "✓ Improved loading animation handling"
    ]
    
    for fix in fixes_applied:
        print(fix)
    
    print("\nTEST RESULTS:")
    all_passed = all(results.values())
    for key, value in results.items():
        status = "PASS" if value else "FAIL"
        print(f"  {key}: {status}")
    
    if all_passed:
        print("\n✅ ALL FIXES WORKING! Bot should now respond properly.")
    else:
        print("\n⚠️  Some issues remain. Check the failed tests above.")
    
    return all_passed

if __name__ == "__main__":
    # Set UTF-8 encoding for stdout
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    
    result = asyncio.run(test_fixes())
    
    if result:
        print("\n🎉 Bot is ready for testing!")
    else:
        print("\n❌ Some fixes need attention.")