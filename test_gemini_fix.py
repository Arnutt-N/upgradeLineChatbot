#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Gemini Service Fix
ทดสอบการแก้ไข Gemini Service
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service, get_ai_response

async def test_gemini_service():
    print("=== Testing Gemini Service Fix ===")
    
    # Test basic availability
    print(f"Service available: {gemini_service.is_available()}")
    
    if not gemini_service.is_available():
        print("❌ Gemini service not available")
        return False
    
    # Test simple text generation
    print("\n--- Testing Simple Text Generation ---")
    try:
        result = await gemini_service.generate_response(
            user_message="สวัสดีครับ คุณชื่ออะไร",
            user_id="test_user_123"
        )
        
        print(f"Success: {result['success']}")
        print(f"Response: {result['response']}")
        
        if result['success'] and result['response']:
            print("[OK] Simple text generation working!")
        else:
            print("[ERROR] Simple text generation failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error in simple generation: {e}")
        return False
    
    # Test helper function
    print("\n--- Testing Helper Function ---")
    try:
        response = await get_ai_response(
            user_message="อธิบายเกี่ยวกับการบริการภาครัฐ",
            user_id="test_user_456"
        )
        
        print(f"Helper response: {response}")
        
        if response and "ขออภัย" not in response:
            print("[OK] Helper function working!")
        else:
            print("[ERROR] Helper function failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error in helper function: {e}")
        return False
    
    # Test smart reply with profile
    print("\n--- Testing Smart Reply ---")
    try:
        user_profile = {
            "user_id": "test_user_789",
            "display_name": "นายทดสอบ",
            "picture_url": None
        }
        
        result = await gemini_service.generate_smart_reply(
            user_message="ขอข้อมูลเกี่ยวกับการขอหนังสือเดินทาง",
            user_profile=user_profile,
            db=None  # No DB for this test
        )
        
        print(f"Smart reply success: {result['success']}")
        print(f"Smart reply response: {result['response']}")
        
        if result['success'] and result['response']:
            print("[OK] Smart reply working!")
            return True
        else:
            print("[ERROR] Smart reply failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error in smart reply: {e}")
        return False

def test_encoding():
    print("\n--- Testing Thai Encoding ---")
    test_text = "สวัสดีครับ ทดสอบภาษาไทย"
    try:
        encoded = test_text.encode('utf-8').decode('utf-8')
        print(f"Original: {test_text}")
        print(f"Encoded/Decoded: {encoded}")
        print("[OK] Encoding test passed!")
        return True
    except Exception as e:
        print(f"[ERROR] Encoding test failed: {e}")
        return False

async def main():
    print("Testing Gemini Service Fix\n")
    
    # Test encoding first
    encoding_ok = test_encoding()
    
    # Test service
    service_ok = await test_gemini_service()
    
    print(f"\n=== Final Result ===")
    print(f"Encoding: {'[OK]' if encoding_ok else '[ERROR]'}")
    print(f"Service: {'[OK]' if service_ok else '[ERROR]'}")
    
    if encoding_ok and service_ok:
        print("[SUCCESS] All tests passed! Gemini service is working properly.")
        return True
    else:
        print("[FAILED] Some tests failed. Check the issues above.")
        return False

if __name__ == '__main__':
    asyncio.run(main())