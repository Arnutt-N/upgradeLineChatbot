# -*- coding: utf-8 -*-
"""
Test script to verify display name functionality
"""
import sqlite3
import os

def test_display_names():
    """Test display name functionality"""
    db_path = "D:/hrProject/upgradeLineChatbot/chatbot.db"
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== Current User Status Table ===")
        cursor.execute("SELECT user_id, display_name, is_in_live_chat, chat_mode FROM user_status")
        users = cursor.fetchall()
        
        for user in users:
            print(f"User ID: {user[0]}")
            print(f"Display Name: {user[1]}")
            print(f"In Live Chat: {user[2]}")
            print(f"Chat Mode: {user[3]}")
            print("-" * 40)
        
        print("\n=== Latest Chat Messages ===")
        cursor.execute("""
            SELECT user_id, sender_type, message, created_at 
            FROM chat_messages 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        messages = cursor.fetchall()
        
        for msg in messages:
            try:
                message_preview = str(msg[2])[:50] if msg[2] else "No message"
                # Remove emojis and non-ASCII characters
                message_clean = ''.join(char for char in message_preview if ord(char) < 128)
                print(f"User: {msg[0][-6:]} | {msg[1]} | {message_clean}...")
            except Exception as e:
                print(f"User: {msg[0][-6:]} | {msg[1]} | [Message encoding error]")
        
        conn.close()
        print("\nDatabase test completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_display_names()
