#!/usr/bin/env python3
"""
Simple test for new system prompt
"""
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_prompt():
    try:
        from app.services.gemini_service import gemini_service
        
        print("Testing new Agent น้อง HR Moj system prompt...")
        
        if not gemini_service.is_available():
            print("Gemini service not available")
            return
        
        result = await gemini_service.generate_response(
            user_message="สวัสดีค่ะ คุณชื่ออะไรคะ",
            user_id="test_user",
            use_session=True
        )
        
        if result['success']:
            response = result['response']
            print(f"Response: {response}")
            
            # Check new character
            has_agent = 'agent' in response.lower() or 'น้อง hr moj' in response.lower()
            has_ja = 'จ้า' in response.lower()
            has_old_neko = 'เนโกะ' in response.lower()
            has_old_meow = 'เมี๊ยว' in response.lower()
            
            print(f"Has Agent/น้อง HR Moj: {has_agent}")
            print(f"Uses 'จ้า': {has_ja}")
            print(f"Has old Neko: {has_old_neko}")
            print(f"Has old Meow: {has_old_meow}")
            
            if has_agent and has_ja and not has_old_neko and not has_old_meow:
                print("SUCCESS: New system prompt working correctly!")
            else:
                print("WARNING: System prompt may need adjustment")
        else:
            print(f"Error: {result.get('error')}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_prompt())