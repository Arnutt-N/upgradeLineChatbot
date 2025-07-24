#!/usr/bin/env python3
"""
Admin Panel Issue Diagnostic Tool
Identifies and diagnoses common issues that prevent the admin panel from working properly
"""

import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_status(item, status, details=""):
    symbol = "✅" if status else "❌"
    print(f"{symbol} {item}")
    if details:
        print(f"   {details}")

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Environment Variables")
    
    required_vars = {
        'LINE_CHANNEL_ACCESS_TOKEN': 'LINE Bot access token',
        'LINE_CHANNEL_SECRET': 'LINE Bot channel secret'
    }
    
    optional_vars = {
        'GEMINI_API_KEY': 'Google Gemini AI API key',
        'TELEGRAM_BOT_TOKEN': 'Telegram bot token',
        'TELEGRAM_CHAT_ID': 'Telegram chat ID for notifications'
    }
    
    all_good = True
    
    # Check required variables
    print("Required Environment Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print_status(f"{var}", True, f"{description} - Set")
        else:
            print_status(f"{var}", False, f"{description} - MISSING!")
            all_good = False
    
    # Check optional variables
    print("\nOptional Environment Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_status(f"{var}", True, f"{description} - Set")
        else:
            print_status(f"{var}", False, f"{description} - Not set (features will be disabled)")
    
    return all_good

def check_database():
    """Check database file and table structure"""
    print_header("Database Status")
    
    db_path = "chatbot.db"
    
    if not Path(db_path).exists():
        print_status("Database file", False, f"{db_path} does not exist")
        return False
    
    print_status("Database file", True, f"{db_path} exists")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check required tables
        required_tables = ['user_status', 'chat_messages']
        optional_tables = ['chat_history', 'friend_activity', 'telegram_notifications']
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("\nRequired Tables:")
        tables_ok = True
        for table in required_tables:
            exists = table in existing_tables
            print_status(f"Table: {table}", exists)
            if not exists:
                tables_ok = False
        
        print("\nOptional Tables (Enhanced features):")
        for table in optional_tables:
            exists = table in existing_tables
            print_status(f"Table: {table}", exists, "Enhanced tracking" if exists else "Basic mode only")
        
        # Check data counts
        print("\nData Statistics:")
        if 'user_status' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM user_status")
            user_count = cursor.fetchone()[0]
            print_status("Users in database", user_count > 0, f"{user_count} users")
        
        total_messages = 0
        if 'chat_messages' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM chat_messages")
            old_messages = cursor.fetchone()[0]
            total_messages += old_messages
            print_status("Messages in chat_messages", True, f"{old_messages} messages")
        
        if 'chat_history' in existing_tables:
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            new_messages = cursor.fetchone()[0]
            total_messages += new_messages
            print_status("Messages in chat_history", True, f"{new_messages} messages")
        
        print_status("Total messages", total_messages > 0, f"{total_messages} total messages")
        
        conn.close()
        return tables_ok
        
    except Exception as e:
        print_status("Database access", False, f"Error: {e}")
        return False

def check_python_dependencies():
    """Check if required Python packages are installed"""
    print_header("Python Dependencies")
    
    required_packages = [
        ('fastapi', 'FastAPI framework'),
        ('sqlalchemy', 'Database ORM'),
        ('aiofiles', 'Async file operations'),
        ('jinja2', 'Template engine'),
        ('line-bot-sdk', 'LINE Bot SDK'),
    ]
    
    optional_packages = [
        ('google-generativeai', 'Google Gemini AI'),
        ('aiohttp', 'HTTP client for testing'),
        ('websockets', 'WebSocket support'),
    ]
    
    deps_ok = True
    
    print("Required Dependencies:")
    for package, description in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(package, True, description)
        except ImportError:
            print_status(package, False, f"{description} - MISSING!")
            deps_ok = False
    
    print("\nOptional Dependencies:")
    for package, description in optional_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(package, True, description)
        except ImportError:
            print_status(package, False, f"{description} - Not installed (feature disabled)")
    
    return deps_ok

def check_file_structure():
    """Check if required files and directories exist"""
    print_header("File Structure")
    
    required_files = [
        'app/main.py',
        'app/api/routers/admin.py',
        'app/services/ws_manager.py',
        'app/db/database.py',
        'templates/admin.html'
    ]
    
    structure_ok = True
    
    for file_path in required_files:
        exists = Path(file_path).exists()
        print_status(file_path, exists)
        if not exists:
            structure_ok = False
    
    return structure_ok

def check_gemini_ai_setup():
    """Check Gemini AI setup specifically"""
    print_header("Gemini AI Setup")
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print_status("Gemini API Key", False, "Not configured - AI features will be disabled")
        return False
    
    print_status("Gemini API Key", True, "Configured")
    
    try:
        import google.generativeai as genai
        print_status("Google AI Library", True, "Installed")
        
        # Try to configure (without making actual API calls)
        try:
            genai.configure(api_key=api_key)
            print_status("Gemini Configuration", True, "API key format valid")
            return True
        except Exception as e:
            print_status("Gemini Configuration", False, f"Configuration error: {e}")
            return False
    except ImportError:
        print_status("Google AI Library", False, "Not installed - run: pip install google-generativeai")
        return False

def generate_recommendations(env_ok, db_ok, deps_ok, files_ok, gemini_ok):
    """Generate recommendations based on check results"""
    print_header("Recommendations")
    
    if all([env_ok, db_ok, deps_ok, files_ok]):
        print("🎉 All critical checks passed! Admin panel should work correctly.")
        if not gemini_ok:
            print("⚠️  Note: AI features will be disabled without Gemini configuration.")
        return
    
    print("🔧 Issues found that need to be addressed:")
    
    if not env_ok:
        print("\n📝 Environment Variables:")
        print("   - Create a .env file in the project root")
        print("   - Add LINE_CHANNEL_ACCESS_TOKEN=your_token_here")
        print("   - Add LINE_CHANNEL_SECRET=your_secret_here")
        print("   - Get these from LINE Developers Console: https://developers.line.biz/")
    
    if not db_ok:
        print("\n📝 Database:")
        print("   - Run the application once to create the database: python app/main.py")
        print("   - Or run migrations: python run_migration.py")
        print("   - Check if the database file has proper permissions")
    
    if not deps_ok:
        print("\n📝 Dependencies:")
        print("   - Install missing packages: pip install -r requirements.txt")
        print("   - Or install individually: pip install fastapi sqlalchemy aiofiles")
    
    if not files_ok:
        print("\n📝 File Structure:")
        print("   - Ensure you're running from the correct directory")
        print("   - Check if all application files are present")
        print("   - Re-download the project if files are missing")
    
    if not gemini_ok:
        print("\n📝 Gemini AI (Optional):")
        print("   - Install Google AI: pip install google-generativeai")
        print("   - Get API key from: https://makersuite.google.com/app/apikey")
        print("   - Add GEMINI_API_KEY=your_api_key to .env file")

def main():
    """Main diagnostic function"""
    print("🏥 Admin Panel Diagnostic Tool")
    print(f"⏰ Run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all checks
    env_ok = check_environment_variables()
    db_ok = check_database()
    deps_ok = check_python_dependencies()
    files_ok = check_file_structure()
    gemini_ok = check_gemini_ai_setup()
    
    # Generate recommendations
    generate_recommendations(env_ok, db_ok, deps_ok, files_ok, gemini_ok)
    
    # Final status
    critical_checks = [env_ok, db_ok, deps_ok, files_ok]
    if all(critical_checks):
        print("\n✅ System ready! You can start the server with: python app/main.py")
    else:
        failed_count = len([x for x in critical_checks if not x])
        print(f"\n❌ {failed_count} critical issues found. Fix them before starting the server.")
    
    return all(critical_checks)

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)