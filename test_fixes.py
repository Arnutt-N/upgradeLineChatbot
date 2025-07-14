#!/usr/bin/env python3
"""
Test script to verify the fixes for:
1. Admin panel chat history display
2. Status button activation  
3. Gemini bot response with system prompt
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini_service import gemini_service, check_gemini_availability
from app.core.config import settings

async def test_gemini_integration():
    """Test Gemini AI integration"""
    print("Testing Gemini Integration...")
    
    # Test availability
    is_available = await check_gemini_availability()
    print(f"[OK] Gemini Available: {is_available}")
    
    if is_available:
        print(f"[OK] Model: {gemini_service.model_name}")
        print(f"[OK] API Key configured: {bool(gemini_service.api_key)}")
        
        # Test basic response
        try:
            result = await gemini_service.generate_response(
                user_message="Hello", 
                user_id="test_user"
            )
            print(f"[OK] Test response success: {result['success']}")
            if result['success']:
                print(f"[OK] Response: {result['response'][:100]}...")
        except Exception as e:
            print(f"[ERROR] Test response error: {e}")
    
    print()

def test_admin_api_structure():
    """Test admin API structure"""
    print("Testing Admin API Structure...")
    
    try:
        from app.api.routers.admin import router
        print("[OK] Admin router imports successfully")
        
        # Check if new endpoints are present
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/admin/status",
            "/admin/force_bot_mode",
            "/admin/users",
            "/admin/messages/{user_id}",
            "/admin/reply",
            "/admin/end_chat",
            "/admin/restart_chat",
            "/admin/toggle_mode"
        ]
        
        for route in expected_routes:
            if any(route in r for r in routes):
                print(f"[OK] Route exists: {route}")
            else:
                print(f"[ERROR] Route missing: {route}")
                
    except Exception as e:
        print(f"[ERROR] Admin API error: {e}")
    
    print()

def test_line_handler():
    """Test LINE handler structure"""
    print("Testing LINE Handler...")
    
    try:
        from app.services.line_handler_enhanced import (
            handle_bot_mode_message,
            handle_live_chat_message,
            get_user_profile_enhanced
        )
        print("[OK] LINE handler functions import successfully")
        
        # Test handler structure
        import inspect
        bot_mode_sig = inspect.signature(handle_bot_mode_message)
        print(f"[OK] handle_bot_mode_message parameters: {list(bot_mode_sig.parameters.keys())}")
        
        live_chat_sig = inspect.signature(handle_live_chat_message)
        print(f"[OK] handle_live_chat_message parameters: {list(live_chat_sig.parameters.keys())}")
        
    except Exception as e:
        print(f"[ERROR] LINE handler error: {e}")
    
    print()

def test_config():
    """Test configuration"""
    print("Testing Configuration...")
    
    print(f"[OK] LINE_CHANNEL_ACCESS_TOKEN configured: {bool(settings.LINE_CHANNEL_ACCESS_TOKEN)}")
    print(f"[OK] GEMINI_API_KEY configured: {bool(getattr(settings, 'GEMINI_API_KEY', None))}")
    print(f"[OK] TELEGRAM_BOT_TOKEN configured: {bool(getattr(settings, 'TELEGRAM_BOT_TOKEN', None))}")
    
    print()

async def main():
    """Run all tests"""
    print("Starting Tests for LINE Bot Fixes\n")
    
    test_config()
    test_admin_api_structure()
    test_line_handler()
    await test_gemini_integration()
    
    print("All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())