#!/usr/bin/env python3
"""
🔐 SECRET_KEY Generator for LINE Chatbot Project
สร้าง SECRET_KEY สำหรับใช้ใน environment variables
"""

import secrets
import string
import pyperclip  # pip install pyperclip (optional)

def generate_secret_keys():
    """สร้าง SECRET_KEY หลายรูปแบบ"""
    
    print("🔐 SECRET_KEY Generator for FastAPI")
    print("=" * 60)
    print()
    
    # Generate different types
    hex_32 = secrets.token_hex(32)  # 64 chars
    hex_64 = secrets.token_hex(64)  # 128 chars
    urlsafe = secrets.token_urlsafe(32)  # ~43 chars
    
    # Custom alphanumeric
    alphabet = string.ascii_letters + string.digits
    alphanumeric = ''.join(secrets.choice(alphabet) for _ in range(64))
    
    print("📋 เลือก SECRET_KEY ที่ต้องการ:\n")
    
    print("1️⃣ Standard (Recommended):")
    print(f"   {hex_32}")
    print(f"   Length: {len(hex_32)} chars\n")
    
    print("2️⃣ Extra Strong:")
    print(f"   {hex_64}")
    print(f"   Length: {len(hex_64)} chars\n")
    
    print("3️⃣ URL-Safe Base64:")
    print(f"   {urlsafe}")
    print(f"   Length: {len(urlsafe)} chars\n")
    
    print("4️⃣ Alphanumeric Only:")
    print(f"   {alphanumeric}")
    print(f"   Length: {len(alphanumeric)} chars\n")
    
    # User selection
    while True:
        choice = input("เลือกหมายเลข (1-4) หรือ Enter สำหรับ default [1]: ").strip()
        if not choice:
            choice = "1"
        
        if choice == "1":
            selected = hex_32
            break
        elif choice == "2":
            selected = hex_64
            break
        elif choice == "3":
            selected = urlsafe
            break
        elif choice == "4":
            selected = alphanumeric
            break
        else:
            print("❌ กรุณาเลือก 1-4")
    
    print(f"\n✅ SECRET_KEY ที่เลือก:")
    print(f"   {selected}")
    
    # Try to copy to clipboard
    try:
        pyperclip.copy(selected)
        print("\n📋 Copied to clipboard!")
    except:
        print("\n💡 Tip: Install pyperclip เพื่อ copy อัตโนมัติ: pip install pyperclip")
    
    # Show how to use
    print("\n📝 วิธีใช้:")
    print("1. เปิดไฟล์ .env หรือ .env.production")
    print("2. เพิ่มบรรทัดนี้:")
    print(f"   SECRET_KEY={selected}")
    print("\n⚠️  อย่าลืม:")
    print("   - ใส่ .env ใน .gitignore")
    print("   - ไม่ commit SECRET_KEY ลง GitHub")
    print("   - ใช้ค่าที่ต่างกันสำหรับแต่ละ environment")
    
    # Save option
    save = input("\n💾 ต้องการสร้างไฟล์ .env.example? (y/n): ")
    if save.lower() == 'y':
        with open('.env.example.generated', 'w') as f:
            f.write("# Generated Environment Variables Example\n")
            f.write("# Copy this to .env and fill in actual values\n\n")
            f.write(f"SECRET_KEY={selected}\n")
            f.write("DATABASE_URL=your_database_url_here\n")
            f.write("LINE_CHANNEL_SECRET=your_line_channel_secret\n")
            f.write("LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token\n")
            f.write("GEMINI_API_KEY=your_gemini_api_key\n")
        print("✅ Created .env.example.generated")

if __name__ == "__main__":
    generate_secret_keys()
