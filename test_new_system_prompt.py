#!/usr/bin/env python3
"""
Test new system prompt with Agent น้อง HR Moj
"""
import asyncio
import sys
import os

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_new_system_prompt():
    """Test the new system prompt to ensure it works correctly"""
    try:
        from app.services.gemini_service import gemini_service
        
        print("Testing new system prompt - Agent น้อง HR Moj")
        print("=" * 50)
        
        if not gemini_service.is_available():
            print("ERROR: Gemini service not available")
            return
        
        # Test questions to verify new character
        test_messages = [
            "สวัสดีค่ะ คุณชื่ออะไรคะ",
            "ช่วยแนะนำตัวหน่อยค่ะ",
            "อยากทราบเรื่องการขอลาป่วยค่ะ",
            "มีฟอร์มอะไรให้กรอกบ้างคะ"
        ]
        
        user_id = "test_user_new_prompt"
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{i}. Testing: {message}")
            
            result = await gemini_service.generate_response(
                user_message=message,
                user_id=user_id,
                use_session=True
            )
            
            if result['success']:
                response = result['response']
                print(f"   Response: {response[:100]}..." if len(response) > 100 else f"   Response: {response}")
                
                # Check for new character traits
                has_agent_name = 'agent' in response.lower() or 'น้อง hr moj' in response.lower()
                has_ja_ending = 'จ้า' in response.lower()
                has_female_particles = any(p in response.lower() for p in ['ค่ะ', 'คะ', 'นะคะ'])
                has_ministry_context = any(word in response.lower() for word in ['กระทรวงยุติธรรม', 'ทรัพยากรบุคคล', 'hr'])
                
                print(f"   ✓ Has Agent/น้อง HR Moj reference: {has_agent_name}")
                print(f"   ✓ Uses 'จ้า' ending: {has_ja_ending}")
                print(f"   ✓ Uses female particles: {has_female_particles}")
                print(f"   ✓ Ministry context: {has_ministry_context}")
                
                # Check that old character traits are not present
                has_old_neko = 'เนโกะ' in response.lower()
                has_old_meow = 'เมี๊ยว' in response.lower()
                
                if has_old_neko or has_old_meow:
                    print(f"   ⚠️ WARNING: Still has old character traits!")
                    print(f"      Old Neko: {has_old_neko}, Old Meow: {has_old_meow}")
                else:
                    print(f"   ✅ No old character traits detected")
                    
            else:
                print(f"   ERROR: {result.get('error')}")
        
        print("\n" + "=" * 50)
        print("✅ System prompt testing completed!")
        
        # Get session info
        session_info = gemini_service.get_chat_sessions_info()
        print(f"Active sessions: {session_info['active_sessions']}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_system_prompt())