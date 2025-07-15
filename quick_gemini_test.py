#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Gemini API Test
ทดสอบ Gemini API แบบรวดเร็ว
"""

import os
import sys
from dotenv import load_dotenv

def test_gemini():
    print("=== Gemini API Quick Test ===")
    
    # Load environment
    load_dotenv()
    api_key = os.getenv('GEMINI_API_KEY')
    model = os.getenv('GEMINI_MODEL', 'gemini-pro')
    
    print(f"API Key: {api_key[:10] if api_key else 'None'}...")
    print(f"Model: {model}")
    
    if not api_key:
        print("ERROR: No GEMINI_API_KEY found")
        return False
    
    try:
        import google.generativeai as genai
        print("SUCCESS: Library imported")
        
        # Configure
        genai.configure(api_key=api_key)
        print("SUCCESS: API configured")
        
        # Test models
        test_models = ['gemini-pro', 'gemini-1.5-pro', model]
        test_models = list(dict.fromkeys(test_models))  # Remove duplicates
        
        for test_model in test_models:
            print(f"\n--- Testing {test_model} ---")
            try:
                model_obj = genai.GenerativeModel(test_model)
                response = model_obj.generate_content("สวัสดี ตอบสั้นๆ")
                
                if response and response.text:
                    print(f"SUCCESS: {test_model} working!")
                    print(f"Response: {response.text[:100]}")
                    
                    # Update .env if different model works
                    if test_model != model:
                        update_env_model(test_model)
                    return True
                else:
                    print(f"ERROR: {test_model} no response")
            except Exception as e:
                print(f"ERROR: {test_model} failed - {str(e)[:100]}")
        
        return False
        
    except ImportError:
        print("ERROR: google-generativeai not installed")
        print("Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def update_env_model(working_model):
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('GEMINI_MODEL='):
                lines[i] = f'GEMINI_MODEL={working_model}'
                break
        else:
            lines.append(f'GEMINI_MODEL={working_model}')
        
        with open('.env', 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"Updated .env with GEMINI_MODEL={working_model}")
    except Exception as e:
        print(f"Could not update .env: {e}")

if __name__ == '__main__':
    success = test_gemini()
    
    print(f"\n=== Result: {'SUCCESS' if success else 'FAILED'} ===")
    if success:
        print("Gemini API is working!")
        print("You can now restart the server.")
    else:
        print("Gemini API test failed!")
        print("Check your API key and model configuration.")
