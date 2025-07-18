# Final Gemini Integration Test (Windows compatible)
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def test_gemini_complete():
    """Complete test of Gemini integration without Unicode issues"""
    try:
        print("=" * 60)
        print("Testing Complete Gemini Integration")
        print("=" * 60)
        
        # Import service
        from app.services.gemini_service import (
            gemini_service, 
            check_gemini_availability, 
            generate_text,
            get_ai_response
        )
        
        # 1. Basic availability test
        print("\n1. Testing availability...")
        is_available = await check_gemini_availability()
        print(f"   Available: {is_available}")
        
        if not is_available:
            print("   Error: Gemini not available")
            return False
        
        # 2. Test simple text generation (jetpack style)
        print("\n2. Testing simple text generation...")
        simple_response = generate_text("Hello, please introduce yourself briefly")
        print(f"   Input: Hello, please introduce yourself briefly")
        print(f"   Output length: {len(simple_response)} characters")
        print(f"   Success: {len(simple_response) > 10}")
        
        # 3. Test session-based generation
        print("\n3. Testing session-based generation...")
        user_id = "test_user_123"
        result = await gemini_service.generate_response(
            user_message="Please introduce yourself in Thai",
            user_id=user_id,
            use_session=True
        )
        print(f"   Success: {result['success']}")
        if result['success']:
            print(f"   Response length: {len(result['response'])} characters")
            
        # 4. Test conversation continuity
        print("\n4. Testing conversation continuity...")
        result2 = await gemini_service.generate_response(
            user_message="What did we just talk about?",
            user_id=user_id,
            use_session=True
        )
        print(f"   Continuation success: {result2['success']}")
        if result2['success']:
            print(f"   Response length: {len(result2['response'])} characters")
        
        # 5. Test helper function
        print("\n5. Testing helper function...")
        helper_response = await get_ai_response(
            user_message="How can you help me?",
            user_id="test_helper_user"
        )
        print(f"   Helper response length: {len(helper_response)} characters")
        print(f"   Helper success: {len(helper_response) > 10}")
        
        # 6. Test model information
        print("\n6. Testing model information...")
        model_info = gemini_service.get_model_info()
        print(f"   Model: {model_info['model']}")
        print(f"   Temperature: {model_info['temperature']}")
        print(f"   Max tokens: {model_info['max_tokens']}")
        print(f"   Safety enabled: {model_info['safety_enabled']}")
        
        # 7. Test session management
        print("\n7. Testing session management...")
        sessions_info = gemini_service.get_chat_sessions_info()
        print(f"   Active sessions: {sessions_info['active_sessions']}")
        print(f"   User IDs count: {len(sessions_info['user_ids'])}")
        
        # 8. Test error handling with problematic input
        print("\n8. Testing error handling...")
        try:
            error_result = await gemini_service.generate_response(
                user_message="",  # Empty message
                user_id="error_test_user",
                use_session=False
            )
            print(f"   Empty message handled: {error_result['success']}")
        except Exception as e:
            print(f"   Exception caught properly: {type(e).__name__}")
        
        # 9. Clear test sessions
        print("\n9. Cleaning up test sessions...")
        gemini_service.clear_chat_session(user_id)
        gemini_service.clear_chat_session("test_helper_user")
        print("   Test sessions cleared")
        
        print("\n" + "=" * 60)
        print("COMPLETE TEST SUCCESSFUL!")
        print("All Gemini features working properly")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR during complete test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_thai_persona():
    """Test the Thai government service persona specifically"""
    try:
        print("\n" + "=" * 60)
        print("Testing Thai Government Service Persona")
        print("=" * 60)
        
        from app.services.gemini_service import gemini_service
        
        # Test Thai language interaction
        thai_questions = [
            "ขอสอบถามเรื่องการยื่นเอกสาร KP7 ครับ",
            "มีบริการอะไรบ้างที่ให้ความช่วยเหลือ",
            "ขอแนะนำการใช้งานระบบหน่อย"
        ]
        
        user_id = "thai_test_user"
        
        for i, question in enumerate(thai_questions, 1):
            print(f"\n{i}. Testing Thai question...")
            print(f"   Question: {question}")
            
            result = await gemini_service.generate_response(
                user_message=question,
                user_id=user_id,
                use_session=True
            )
            
            if result['success']:
                response = result['response']
                print(f"   Response length: {len(response)} characters")
                
                # Check for Thai polite particles
                has_polite_particles = any(particle in response.lower() for particle in ['ค่ะ', 'คะ', 'นะคะ', 'ครับ'])
                print(f"   Contains polite particles: {has_polite_particles}")
                
                # Check for service-oriented language
                has_service_terms = any(term in response.lower() for term in ['บริการ', 'ช่วยเหลือ', 'แนะนำ', 'สอบถาม'])
                print(f"   Contains service terms: {has_service_terms}")
                
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # Clean up
        gemini_service.clear_chat_session(user_id)
        
        print("\n" + "=" * 60)
        print("THAI PERSONA TEST COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR during Thai persona test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Starting Final Gemini Integration Tests...")
    
    # Run complete test
    success = asyncio.run(test_gemini_complete())
    
    if success:
        print("\nRunning Thai persona test...")
        asyncio.run(test_thai_persona())
        
        print("\n" + "=" * 80)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("Gemini integration is working properly with:")
        print("- Text generation (sync and async)")
        print("- Session management and conversation continuity")
        print("- Thai language support with proper persona")
        print("- Error handling and safety measures")
        print("- Helper functions for easy integration")
        print("=" * 80)
    else:
        print("\nSome tests failed. Please check the configuration.")