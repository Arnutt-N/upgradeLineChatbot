#!/usr/bin/env python3
"""Quick test for bot functionality after merge"""

import asyncio
import sys
import os
from fastapi.testclient import TestClient

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.db.database import get_db
from app.services.line_handler_enhanced import handle_message_enhanced

async def test_basic_functionality():
    """Test basic bot functionality"""
    
    # Test 1: Check if app loads
    client = TestClient(app)
    print("TESTING: App initialization...")
    response = client.get("/health")
    print(f"Health check: {response.status_code}")
    if response.status_code == 200:
        print("PASS: App initialization")
    else:
        print("FAIL: App initialization")
        return False
    
    # Test 2: Check webhook endpoint
    print("\nTESTING: Webhook endpoint...")
    response = client.get("/webhook")
    print(f"Webhook endpoint: {response.status_code}")
    if response.status_code in [200, 405]:  # Either verification or method not allowed
        print("PASS: Webhook endpoint exists")
    else:
        print("FAIL: Webhook endpoint")
        return False
    
    # Test 3: Check admin endpoint
    print("\nTESTING: Admin endpoint...")
    response = client.get("/admin")
    print(f"Admin endpoint: {response.status_code}")
    if response.status_code == 200:
        print("PASS: Admin endpoint")
    else:
        print("FAIL: Admin endpoint")
        return False
        
    # Test 4: Check if we can import critical services
    print("\nTESTING: Service imports...")
    try:
        from app.services.gemini_service import gemini_service
        print("PASS: Gemini service")
    except Exception as e:
        print(f"FAIL: Gemini service - {e}")
        
    try:
        from app.services.ws_manager import manager
        print("PASS: WebSocket manager")
    except Exception as e:
        print(f"FAIL: WebSocket manager - {e}")
        
    try:
        from app.db.crud_enhanced import save_chat_to_history
        print("PASS: Database functions")
    except Exception as e:
        print(f"FAIL: Database functions - {e}")
    
    print("\nBasic functionality test completed!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_basic_functionality())
    except Exception as e:
        print(f"FAIL: Test failed with error: {e}")
        sys.exit(1)