import sqlite3

print("Checking current users in database...")
print("=" * 40)

try:
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    # ตรวจสอบ users ทั้งหมด
    cursor.execute("SELECT user_id, display_name, picture_url FROM user_status")
    all_users = cursor.fetchall()
    
    print(f"Total users: {len(all_users)}")
    print()
    
    if len(all_users) == 0:
        print("No users found in database.")
    else:
        print("Current users:")
        for i, user in enumerate(all_users, 1):
            user_id, display_name, picture_url = user
            pic_status = "Has Picture" if picture_url else "No Picture"
            print(f"{i}. {user_id}")
            print(f"   Name: {display_name or 'NULL'}")
            print(f"   Picture: {pic_status}")
            if picture_url:
                print(f"   URL: {picture_url[:50]}...")
            print()
    
    # นับ users ที่ไม่มีรูป
    cursor.execute("""
        SELECT COUNT(*) FROM user_status 
        WHERE picture_url IS NULL OR picture_url = ''
    """)
    no_picture_count = cursor.fetchone()[0]
    
    print(f"Users without pictures: {no_picture_count}")
    
    if no_picture_count > 0:
        print()
        print("These users need avatar backfill:")
        cursor.execute("""
            SELECT user_id, display_name FROM user_status 
            WHERE picture_url IS NULL OR picture_url = ''
        """)
        
        for user in cursor.fetchall():
            user_id, display_name = user
            print(f"- {user_id}: {display_name or 'No name'}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
