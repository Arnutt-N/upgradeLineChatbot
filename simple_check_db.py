import sqlite3
import sys

print("🔍 Checking database schema...")
print("=" * 40)

try:
    # เชื่อมต่อฐานข้อมูล
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    # ตรวจสอบ schema ปัจจุบัน
    cursor.execute("PRAGMA table_info(user_status)")
    columns = cursor.fetchall()
    
    print("📊 Current user_status table columns:")
    column_names = []
    for i, col in enumerate(columns, 1):
        col_name = col[1]
        col_type = col[2]
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        print(f"  {i}. {col_name}: {col_type} ({nullable})")
        column_names.append(col_name)
    
    # ตรวจสอบ picture_url
    print(f"\n🔍 Checking for picture_url column...")
    if "picture_url" in column_names:
        print("✅ picture_url column already EXISTS!")
    else:
        print("❌ picture_url column NOT FOUND!")
        print("📝 Adding picture_url column...")
        
        try:
            cursor.execute("ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL")
            conn.commit()
            print("✅ Successfully added picture_url column!")
            
            # ตรวจสอบอีกครั้ง
            cursor.execute("PRAGMA table_info(user_status)")
            new_columns = cursor.fetchall()
            print(f"\n📊 Updated schema ({len(new_columns)} columns):")
            for i, col in enumerate(new_columns, 1):
                col_name = col[1]
                col_type = col[2]
                nullable = "NULL" if col[3] == 0 else "NOT NULL"
                print(f"  {i}. {col_name}: {col_type} ({nullable})")
                
        except Exception as e:
            print(f"❌ Error adding column: {e}")
    
    # แสดงสถิติข้อมูล
    cursor.execute("SELECT COUNT(*) FROM user_status")
    total_users = cursor.fetchone()[0]
    print(f"\n📈 Database statistics:")
    print(f"  - Total users: {total_users}")
    
    if total_users > 0:
        cursor.execute("SELECT user_id, display_name, picture_url FROM user_status LIMIT 3")
        sample_data = cursor.fetchall()
        print(f"  - Sample data:")
        for user in sample_data:
            user_id = user[0]
            display_name = user[1] or "N/A"
            picture_url = user[2] or "NULL"
            print(f"    * {user_id}: {display_name} (pic: {picture_url})")
    
    conn.close()
    print(f"\n🎉 Database check completed successfully!")
    
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)
