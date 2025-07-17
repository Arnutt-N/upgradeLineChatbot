# Test Gemini Jetpack Integration
"""
Test script to verify the new Gemini integration with jetpack-style API
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_gemini_integration():
    """Test the new Gemini integration"""
    try:
        # Test basic availability
        from app.services.gemini_service import gemini_service, check_gemini_availability, generate_text
        
        print("=" * 60)
        print("🧪 Testing Gemini Jetpack Integration")
        print("=" * 60)
        
        # 1. Test service availability
        print("\n1. Testing service availability...")
        is_available = await check_gemini_availability()
        print(f"   ✓ Gemini available: {is_available}")
        
        if not is_available:
            print("   ❌ Gemini not available - check API key and configuration")
            return
        
        # 2. Test basic text generation (jetpack style)
        print("\n2. Testing basic text generation (jetpack style)...")
        test_message = "สวัสดีค่ะ ช่วยแนะนำบริการได้ไหม"
        response = generate_text(test_message)
        print(f"   Input: {test_message}")
        print(f"   Output: {response[:100]}...")
        
        # 3. Test session-based generation
        print("\n3. Testing session-based generation...")
        user_id = "test_user_123"
        result = await gemini_service.generate_response(
            user_message="หวัดดีครับ",
            user_id=user_id,
            use_session=True
        )
        print(f"   Session response success: {result['success']}")
        if result['success']:
            print(f"   Response: {result['response'][:100]}...")
        
        # 4. Test conversation continuity
        print("\n4. Testing conversation continuity...")
        result2 = await gemini_service.generate_response(
            user_message="ช่วยเล่าต่อเรื่องที่เราคุยกันไว้หน่อย",
            user_id=user_id,
            use_session=True
        )
        print(f"   Continuation response success: {result2['success']}")
        if result2['success']:
            print(f"   Response: {result2['response'][:100]}...")
        
        # 5. Test model info
        print("\n5. Testing model information...")
        model_info = gemini_service.get_model_info()
        print(f"   Model: {model_info['model']}")
        print(f"   API Type: {model_info['api_type']}")
        print(f"   Chat Sessions: {model_info['chat_sessions']}")
        
        # 6. Test image analysis availability (without actual image)
        print("\n6. Testing image analysis availability...")
        try:
            from app.services.gemini_service import image_understanding
            print("   ✓ Image analysis function available")
        except ImportError as e:
            print(f"   ❌ Image analysis not available: {e}")
        
        # 7. Test document analysis availability (without actual document)
        print("\n7. Testing document analysis availability...")
        try:
            from app.services.gemini_service import document_understanding
            print("   ✓ Document analysis function available")
        except ImportError as e:
            print(f"   ❌ Document analysis not available: {e}")
        
        # 8. Test session management
        print("\n8. Testing session management...")
        sessions_info = gemini_service.get_chat_sessions_info()
        print(f"   Active sessions: {sessions_info['active_sessions']}")
        print(f"   User IDs: {sessions_info['user_ids']}")
        
        # Clear test session
        gemini_service.clear_chat_session(user_id)
        print(f"   ✓ Cleared test session for {user_id}")
        
        print("\n" + "=" * 60)
        print("✅ Gemini Jetpack Integration Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

async def test_specific_features():
    """Test specific jetpack-style features"""
    try:
        from app.services.gemini_service import gemini_service
        
        print("\n" + "=" * 60)
        print("🔬 Testing Specific Jetpack Features")
        print("=" * 60)
        
        # Test Thai government service persona
        print("\n1. Testing Thai government service persona...")
        user_profile = {
            "user_id": "test_gov_user",
            "display_name": "คุณสมชาย"
        }
        
        # Simulate database session (for testing only)
        class MockDB:
            pass
        
        result = await gemini_service.generate_smart_reply(
            user_message="ขอทราบเรื่องการยื่นเอกสาร KP7 หน่อยครับ",
            user_profile=user_profile,
            db=MockDB()
        )
        
        if result['success']:
            print(f"   ✓ Government service response: {result['response'][:150]}...")
        else:
            print(f"   ❌ Failed: {result.get('error')}")
        
        # Test cute female persona characteristics
        print("\n2. Testing cute female persona...")
        result2 = await gemini_service.generate_response(
            user_message="เมื่อไหร่จะมีการอัปเดตระบบใหม่",
            user_id="test_persona_user",
            use_session=True
        )
        
        if result2['success']:
            response = result2['response']
            print(f"   Response: {response}")
            
            # Check for female polite particles
            has_female_particles = any(particle in response for particle in ['ค่ะ', 'คะ', 'นะคะ'])
            print(f"   ✓ Uses female polite particles: {has_female_particles}")
            
            # Check for cute/friendly tone
            has_friendly_tone = any(word in response for word in ['จ้า', '😊', '💕', 'นะ'])
            print(f"   ✓ Has friendly/cute tone: {has_friendly_tone}")
        
        print("\n✅ Specific Features Test Complete!")
        
    except Exception as e:
        print(f"\n❌ Error during specific features testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Gemini Jetpack Integration Tests...")
    
    # Run tests
    asyncio.run(test_gemini_integration())
    asyncio.run(test_specific_features())
    
    print("\n🎉 All tests completed!")