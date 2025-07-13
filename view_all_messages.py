#!/usr/bin/env python3
"""
Script to view all messages from LINE chatbot users in both manual and bot modes
Analyzes message flow and Gemini AI integration
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List

def analyze_chat_database():
    """Comprehensive analysis of all chat data"""
    
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()
    
    print("=" * 80)
    print("🤖 LINE CHATBOT MESSAGE ANALYSIS")
    print("=" * 80)
    
    # 1. User Status Analysis
    print("\n📊 USER STATUS OVERVIEW")
    print("-" * 40)
    
    cursor.execute("""
        SELECT user_id, display_name, is_in_live_chat, chat_mode, 
               picture_url, created_at, updated_at
        FROM user_status 
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    print(f"Total Users: {len(users)}")
    
    for user in users:
        print(f"\n👤 User: {user[1]}")
        print(f"   ID: {user[0]}")
        print(f"   Mode: {'🔴 Live Chat' if user[2] else '🤖 Bot Mode'} (chat_mode: {user[3]})")
        print(f"   Avatar: {'✅' if user[4] else '❌'}")
        print(f"   Created: {user[5]}")
        print(f"   Updated: {user[6]}")
    
    # 2. Message Count Summary
    print(f"\n📈 MESSAGE STATISTICS")
    print("-" * 40)
    
    # Legacy messages
    cursor.execute("SELECT COUNT(*) FROM chat_messages")
    legacy_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE sender_type = 'user'")
    legacy_user = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_messages WHERE sender_type IN ('bot', 'admin')")
    legacy_bot = cursor.fetchone()[0]
    
    # Enhanced messages  
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    enhanced_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE message_type = 'user'")
    enhanced_user = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE message_type LIKE '%bot%' OR message_type = 'admin'")
    enhanced_bot = cursor.fetchone()[0]
    
    print(f"Legacy Messages (chat_messages): {legacy_count}")
    print(f"  ├─ User messages: {legacy_user}")
    print(f"  └─ Bot/Admin replies: {legacy_bot}")
    print(f"Enhanced Messages (chat_history): {enhanced_count}")
    print(f"  ├─ User messages: {enhanced_user}")
    print(f"  └─ Bot/Admin replies: {enhanced_bot}")
    
    # 3. Recent Chat History Analysis
    print(f"\n💬 RECENT CHAT HISTORY (Enhanced)")
    print("-" * 40)
    
    cursor.execute("""
        SELECT ch.user_id, us.display_name, ch.message_type, 
               ch.message_content, ch.extra_data, ch.timestamp
        FROM chat_history ch
        LEFT JOIN user_status us ON ch.user_id = us.user_id
        ORDER BY ch.timestamp DESC
        LIMIT 20
    """)
    
    messages = cursor.fetchall()
    
    for msg in messages:
        user_name = msg[1] or f"User {msg[0][:8]}..."
        msg_type = msg[2]
        content = msg[3][:60] + "..." if len(msg[3]) > 60 else msg[3]
        timestamp = msg[5]
        
        # Parse extra data for AI info
        ai_info = ""
        if msg[4]:
            try:
                extra = json.loads(msg[4])
                if extra.get('ai_powered'):
                    ai_info = " 🤖"
                elif extra.get('gemini_response'):
                    ai_info = " ✨"
            except:
                pass
        
        # Format message type with emoji
        type_emoji = {
            'user': '👤',
            'bot': '🤖', 
            'ai_bot': '✨',
            'admin': '👨‍💼',
            'user_image': '📸',
            'user_file': '📄'
        }.get(msg_type, '❓')
        
        print(f"{timestamp} | {type_emoji} {msg_type:12} | {user_name:15} | {content}{ai_info}")
    
    # 4. Gemini AI Activity Analysis
    print(f"\n🧠 GEMINI AI ACTIVITY")
    print("-" * 40)
    
    cursor.execute("""
        SELECT COUNT(*) FROM system_logs 
        WHERE category = 'gemini'
    """)
    gemini_logs = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM chat_history 
        WHERE extra_data LIKE '%ai_powered%' OR extra_data LIKE '%gemini%'
    """)
    ai_messages = cursor.fetchone()[0]
    
    print(f"Gemini System Logs: {gemini_logs}")
    print(f"AI-Powered Messages: {ai_messages}")
    
    if gemini_logs > 0:
        cursor.execute("""
            SELECT subcategory, message, timestamp 
            FROM system_logs 
            WHERE category = 'gemini' 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        logs = cursor.fetchall()
        
        print("\nRecent Gemini Activity:")
        for log in logs:
            print(f"  {log[2]} | {log[0]:20} | {log[1][:50]}...")
    
    # 5. Message Flow Analysis
    print(f"\n🔄 MESSAGE FLOW ANALYSIS")
    print("-" * 40)
    
    # Check for conversations without responses
    cursor.execute("""
        SELECT us.display_name, COUNT(*) as user_msgs,
               (SELECT COUNT(*) FROM chat_history ch2 
                WHERE ch2.user_id = ch.user_id 
                AND ch2.message_type IN ('bot', 'ai_bot', 'admin')) as bot_responses
        FROM chat_history ch
        JOIN user_status us ON ch.user_id = us.user_id
        WHERE ch.message_type = 'user'
        GROUP BY ch.user_id, us.display_name
        ORDER BY user_msgs DESC
    """)
    
    conversations = cursor.fetchall()
    
    print("Conversation Summary:")
    for conv in conversations:
        response_ratio = conv[2] / conv[1] if conv[1] > 0 else 0
        status = "✅ Good" if response_ratio > 0.5 else "⚠️ Low Response" if response_ratio > 0 else "❌ No Responses"
        print(f"  {conv[0]:15} | {conv[1]:3} msgs | {conv[2]:3} responses | {status}")
    
    # 6. System Health Check
    print(f"\n🔧 SYSTEM HEALTH CHECK")
    print("-" * 40)
    
    # Check recent system logs for errors
    cursor.execute("""
        SELECT level, category, subcategory, COUNT(*) 
        FROM system_logs 
        WHERE timestamp > datetime('now', '-24 hours')
        GROUP BY level, category, subcategory
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    
    recent_logs = cursor.fetchall()
    
    if recent_logs:
        print("Recent System Activity (24h):")
        for log in recent_logs:
            level_emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}.get(log[0], '📝')
            print(f"  {level_emoji} {log[0]:8} | {log[1]:15} | {log[2]:20} | {log[3]:3} times")
    else:
        print("No recent system logs found")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    analyze_chat_database()