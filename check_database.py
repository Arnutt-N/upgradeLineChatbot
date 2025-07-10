import sqlite3

try:
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    print("📊 Current user_status table schema:")
    cursor.execute("PRAGMA table_info(user_status)")
    columns = cursor.fetchall()
    
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        nullable = "NULL" if col[3] == 0 else "NOT NULL"
        print(f"  - {col_name}: {col_type} ({nullable})")
    
    # ตรวจสอบว่า picture_url มีอยู่หรือไม่
    column_names = [row[1] for row in columns]
    if "picture_url" in column_names:
        print("\n✅ picture_url column EXISTS!")
    else:
        print("\n❌ picture_url column NOT FOUND!")
        print("Attempting to add column...")
        try:
            cursor.execute("ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL")
            conn.commit()
            print("✅ picture_url column added successfully!")
        except Exception as e:
            print(f"❌ Failed to add column: {e}")
    
    # แสดงข้อมูลที่มีอยู่
    cursor.execute("SELECT COUNT(*) FROM user_status")
    count = cursor.fetchone()[0]
    print(f"\n📈 Total users in database: {count}")
    
    conn.close()
    print("\n🎉 Database check completed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
