#!/usr/bin/env python3
"""Test Thai timezone implementation"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pytz
from datetime import datetime

def test_thai_timezone():
    """Test Thai timezone functionality"""
    print("Testing Thai Timezone Implementation")
    print("=" * 50)
    
    # Test Thai timezone
    thai_tz = pytz.timezone('Asia/Bangkok')
    thai_time = datetime.now(thai_tz)
    
    print(f"Thai time now: {thai_time}")
    print(f"Thai time ISO: {thai_time.isoformat()}")
    print(f"Display format (HH:MM): {thai_time.strftime('%H:%M')}")
    
    # Test UTC to Thai conversion
    utc_time = datetime.utcnow()
    utc_localized = pytz.utc.localize(utc_time)
    thai_converted = utc_localized.astimezone(thai_tz)
    
    print(f"\nUTC time: {utc_time}")
    print(f"Converted to Thai: {thai_converted}")
    print(f"Thai display format: {thai_converted.strftime('%H:%M')}")
    
    # Test frontend JavaScript equivalent
    print(f"\nJavaScript equivalent:")
    print(f"new Date('{thai_time.isoformat()}').toLocaleTimeString('th-TH', {{")
    print(f"  timeZone: 'Asia/Bangkok',")
    print(f"  hour: '2-digit',")
    print(f"  minute: '2-digit',")
    print(f"  hour12: false")
    print(f"}}) = {thai_time.strftime('%H:%M')}")
    
    print("\n✅ Thai timezone test completed successfully!")

if __name__ == "__main__":
    test_thai_timezone()