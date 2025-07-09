# patch_for_render.py
# แฟ้มสำหรับแก้ไขปัญหา LINE Bot SDK ใน production

import os
import sys

# เพิ่ม path สำหรับ modules
sys.path.insert(0, '/opt/render/project/src')

# แก้ไข LINE Bot SDK imports
try:
    from linebot.v3.messaging import AsyncMessagingApi
    print("✅ LINE Bot SDK imported successfully")
except ImportError as e:
    print(f"❌ LINE Bot SDK import error: {e}")

# Test function สำหรับ user profile (fallback)
def get_user_display_name(user_id: str) -> str:
    """ฟังก์ชัน fallback สำหรับแสดงชื่อผู้ใช้"""
    return f"ลูกค้า {user_id[-6:]}"

print("🔧 Patch applied for Render deployment")
