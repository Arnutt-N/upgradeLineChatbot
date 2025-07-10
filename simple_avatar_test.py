import sqlite3
import os

print("Testing Avatar System...")

try:
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(user_status)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "picture_url" in columns:
        print("SUCCESS: picture_url column exists")
    else:
        print("ERROR: picture_url column missing")
    
    cursor.execute("SELECT COUNT(*) FROM user_status")
    count = cursor.fetchone()[0]
    print(f"Total users: {count}")
    
    # Test insert
    test_id = "test_avatar_user"
    cursor.execute("DELETE FROM user_status WHERE user_id = ?", (test_id,))
    cursor.execute("""
        INSERT INTO user_status (user_id, display_name, picture_url, is_in_live_chat, chat_mode)
        VALUES (?, ?, ?, ?, ?)
    """, (test_id, "Test User", "https://example.com/pic.jpg", False, "manual"))
    
    conn.commit()
    
    cursor.execute("SELECT display_name, picture_url FROM user_status WHERE user_id = ?", (test_id,))
    result = cursor.fetchone()
    
    if result:
        name, pic_url = result
        print(f"Test user: {name} - {pic_url}")
        print("SUCCESS: Avatar system working")
    else:
        print("ERROR: Could not retrieve test data")
    
    cursor.execute("DELETE FROM user_status WHERE user_id = ?", (test_id,))
    conn.commit()
    conn.close()
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"ERROR: {e}")
