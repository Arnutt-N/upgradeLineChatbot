#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Gemini Service Test - Windows Console Compatible
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_gemini():
    print("Testing Gemini Service")
    
    try:
        from app.services.gemini_service import gemini_service, get_ai_response
        
        # Check availability
        available = gemini_service.is_available()
        print(f"Service available: {available}")
        
        if not available:
            print("Service not available - check API key and configuration")
            return False
        
        # Test simple response
        print("Testing simple response...")
        result = await gemini_service.generate_response(
            user_message="Hello, please respond in Thai",
            user_id="test_user"
        )
        
        print(f"Success: {result['success']}")
        if result['success']:
            response = result['response']
            print(f"Response length: {len(response)} characters")
            # Check if response contains readable text
            if len(response) > 5 and response != "ขออภัย ไม่สามารถประมวลผลคำขอได้ในขณะนี้":
                print("Response received successfully")
                return True
            else:
                print("Response seems invalid")
                return False
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        return False

async def main():
    success = await test_gemini()
    print(f"Test result: {'PASSED' if success else 'FAILED'}")
    return success

if __name__ == '__main__':
    result = asyncio.run(main())
    sys.exit(0 if result else 1)