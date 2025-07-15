#!/usr/bin/env python3
"""
Test Gemini API Configuration
ทดสอบการตั้งค่า Gemini API และแก้ไขปัญหา
"""

import os
import asyncio
from dotenv import load_dotenv

async def test_gemini_api():
    """ทดสอบ Gemini API"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    model_name = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    print("🔍 Testing Gemini API Configuration")
    print("=" * 50)
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"🤖 Model: {model_name}")
    
    try:
        # Import Gemini library
        import google.generativeai as genai
        print("✅ google-generativeai library imported")
        
        # Configure API
        genai.configure(api_key=api_key)
        print("✅ API configured")
        
        # Test with gemini-pro first (most stable)
        test_models = ['gemini-pro', 'gemini-1.5-pro', model_name]
        test_models = list(dict.fromkeys(test_models))  # Remove duplicates
        
        for model in test_models:
            print(f"\n🧪 Testing model: {model}")
            try:
                # Create model
                genai_model = genai.GenerativeModel(model)
                
                # Test simple generation
                response = genai_model.generate_content("สวัสดีครับ ตอบสั้นๆ")
                
                if response and response.text:
                    print(f"✅ {model} working!")
                    print(f"   Response: {response.text[:100]}...")
                    
                    # Update .env file with working model
                    if model != model_name:
                        print(f"💡 Recommend using model: {model}")
                        update_env_model(model)
                    
                    return True
                else:
                    print(f"❌ {model} - No response")
                    
            except Exception as e:
                print(f"❌ {model} failed: {str(e)[:100]}")
                continue
        
        print("\n❌ All models failed")
        return False
        
    except ImportError:
        print("❌ google-generativeai library not installed")
        print("💡 Install with: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def update_env_model(working_model):
    """อัปเดต .env file ด้วย model ที่ใช้ได้"""
    try:
        env_file = ".env"
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Replace or add GEMINI_MODEL
        lines = content.split('\n')
        updated = False
        
        for i, line in enumerate(lines):
            if line.startswith('GEMINI_MODEL='):
                lines[i] = f'GEMINI_MODEL={working_model}'
                updated = True
                break
        
        if not updated:
            lines.append(f'GEMINI_MODEL={working_model}')
        
        with open(env_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Updated .env with GEMINI_MODEL={working_model}")
        
    except Exception as e:
        print(f"⚠️ Could not update .env: {e}")

def check_api_key_validity():
    """ตรวจสอบความถูกต้องของ API key"""
    
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        return False
    
    # Basic format check
    if not api_key.startswith('AIzaSy') or len(api_key) != 39:
        print("⚠️ API key format may be incorrect")
        print("   Expected format: AIzaSy... (39 characters)")
        print(f"   Your key: {api_key[:10]}... ({len(api_key)} characters)")
        return False
    
    return True

async def main():
    print("🚀 Gemini API Diagnostic Tool")
    print("🎯 Purpose: Fix bot fallback responses")
    print()
    
    # Check API key format
    if not check_api_key_validity():
        print("❌ Invalid API key format")
        return
    
    # Test API
    success = await test_gemini_api()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Gemini API is working!")
        print("🔄 Restart your server: python main.py")
        print("📱 Test chat in admin panel")
    else:
        print("❌ Gemini API test failed")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check your API key at https://makersuite.google.com/app/apikey")
        print("2. Verify API quotas and billing")
        print("3. Check internet connection")
        print("4. Try a different model name")
        print("\n💡 Get a new API key:")
        print("   https://ai.google.dev/aistudio")

if __name__ == "__main__":
    asyncio.run(main())
