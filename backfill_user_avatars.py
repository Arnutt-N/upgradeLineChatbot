#!/usr/bin/env python3
# backfill_user_avatars.py - Update existing users with profile pictures
import sys
import os
import sqlite3
import asyncio
import httpx
from datetime import datetime

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.config import settings
    LINE_TOKEN = settings.LINE_CHANNEL_ACCESS_TOKEN
except ImportError:
    # Fallback - read from .env manually
    from dotenv import load_dotenv
    load_dotenv()
    LINE_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')

async def get_line_profile(user_id):
    """ดึงโปรไฟล์จาก LINE API"""
    if not LINE_TOKEN:
        print(f"   [WARNING] No LINE token configured")
        return None, None
    
    try:
        headers = {
            'Authorization': f'Bearer {LINE_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.line.me/v2/bot/profile/{user_id}',
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                display_name = data.get('displayName', None)
                picture_url = data.get('pictureUrl', None)
                print(f"   [OK] Retrieved: {display_name} (pic: {'Yes' if picture_url else 'No'})")
                return display_name, picture_url
            else:
                print(f"   [ERROR] LINE API failed: {response.status_code}")
                return None, None
                
    except Exception as e:
        print(f"   [ERROR] LINE API exception: {e}")
        return None, None

async def backfill_avatars():
    """อัพเดตรูปโปรไฟล์สำหรับ User เก่า"""
    
    print("🔄 Backfilling User Avatars")
    print("=" * 40)
    
    try:
        # เชื่อมต่อฐานข้อมูล
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        
        # ตรวจสอบ users ที่ไม่มี picture_url
        print("1. Checking users without avatars...")
        cursor.execute("""
            SELECT user_id, display_name, picture_url 
            FROM user_status 
            WHERE picture_url IS NULL OR picture_url = ''
        """)
        
        users_without_avatars = cursor.fetchall()
        total_users = len(users_without_avatars)
        
        if total_users == 0:
            print("   [INFO] All users already have avatars!")
            conn.close()
            return
        
        print(f"   [INFO] Found {total_users} users without avatars:")
        for user in users_without_avatars:
            user_id, display_name, picture_url = user
            print(f"   - {user_id}: {display_name or 'No name'} (pic: {picture_url or 'NULL'})")
        
        # อัพเดตทีละคน
        print(f"\n2. Updating avatars for {total_users} users...")
        updated_count = 0
        failed_count = 0
        
        for user in users_without_avatars:
            user_id, display_name, current_pic_url = user
            print(f"\n   Processing: {user_id}")
            
            # ดึงข้อมูลจาก LINE API
            new_display_name, new_picture_url = await get_line_profile(user_id)
            
            # อัพเดตฐานข้อมูล
            updates = []
            params = []
            
            # อัพเดต display_name ถ้าได้ใหม่
            if new_display_name and (not display_name or display_name.startswith("Customer")):
                updates.append("display_name = ?")
                params.append(new_display_name)
                print(f"   [UPDATE] Name: {display_name} → {new_display_name}")
            
            # อัพเดต picture_url ถ้าได้ใหม่
            if new_picture_url:
                updates.append("picture_url = ?")
                params.append(new_picture_url)
                print(f"   [UPDATE] Picture: NULL → Available")
                updated_count += 1
            else:
                print(f"   [SKIP] No picture available from LINE")
                failed_count += 1
            
            # Execute update ถ้ามีการเปลี่ยนแปลง
            if updates:
                params.append(user_id)  # สำหรับ WHERE clause
                sql = f"UPDATE user_status SET {', '.join(updates)} WHERE user_id = ?"
                cursor.execute(sql, params)
                conn.commit()
        
        # สรุปผลลัพธ์
        print(f"\n3. Summary:")
        print(f"   - Total users processed: {total_users}")
        print(f"   - Successfully updated: {updated_count}")
        print(f"   - Failed/No picture: {failed_count}")
        
        # ตรวจสอบผลลัพธ์
        cursor.execute("""
            SELECT COUNT(*) FROM user_status 
            WHERE picture_url IS NOT NULL AND picture_url != ''
        """)
        users_with_avatars = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM user_status")
        total_all_users = cursor.fetchone()[0]
        
        print(f"   - Users with avatars: {users_with_avatars}/{total_all_users}")
        
        # แสดงตัวอย่าง users ที่อัพเดตแล้ว
        if updated_count > 0:
            print(f"\n4. Updated users sample:")
            cursor.execute("""
                SELECT user_id, display_name, 
                       CASE 
                         WHEN picture_url IS NOT NULL THEN 'Has Picture'
                         ELSE 'No Picture'
                       END as avatar_status
                FROM user_status 
                LIMIT 5
            """)
            
            for user in cursor.fetchall():
                user_id, name, avatar_status = user
                print(f"   - {user_id}: {name} ({avatar_status})")
        
        conn.close()
        
        if updated_count > 0:
            print(f"\n✅ Successfully backfilled {updated_count} user avatars!")
        else:
            print(f"\n⚠️ No avatars could be retrieved from LINE API")
            print("   This might be due to:")
            print("   - Invalid LINE access token")
            print("   - Users haven't interacted recently")
            print("   - LINE API limitations")
        
    except Exception as e:
        print(f"\n❌ Error during backfill: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(backfill_avatars())
