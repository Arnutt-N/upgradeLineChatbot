# 🚀 คู่มือการ Deploy LINE Chatbot บน Vercel + Supabase PostgreSQL

## 📋 ภาพรวมระบบ

โปรเจคนี้เป็น LINE Chatbot พร้อมระบบ Admin Panel ที่พัฒนาด้วย FastAPI สำหรับการจัดการแชทและฟอร์มต่างๆ โดยจะ deploy บน Vercel และใช้ Supabase PostgreSQL เป็นฐานข้อมูล

### ✨ Features หลัก
- LINE Bot integration พร้อม Webhook
- Live Chat Admin System
- Form Management System (KP7, ID Card)
- Google Gemini AI Integration
- Real-time WebSocket Communication
- Analytics Dashboard
- User Management

## 1. 🛠️ เตรียมความพร้อมก่อน Deploy

### 1.1 สิ่งที่ต้องมี
- GitHub Account พร้อม repository ของโปรเจค
- Vercel Account (สมัครฟรีที่ vercel.com)
- Supabase Account (สมัครฟรีที่ supabase.com)
- LINE Developer Account
- Google Cloud Account (สำหรับ Gemini API)

### 1.2 API Keys ที่ต้องเตรียม
```
- LINE_CHANNEL_SECRET
- LINE_CHANNEL_ACCESS_TOKEN
- GEMINI_API_KEY
- Database credentials จาก Supabase
```

## 2. 🗄️ ตั้งค่า Supabase PostgreSQL

### 2.1 สร้างโปรเจคใหม่
1. Login ที่ https://supabase.com
2. คลิก "New project"
3. กรอกข้อมูล:
   ```
   Name: linechatbot-db
   Database Password: [สร้าง password ที่แข็งแรง]
   Region: Singapore (sea1)
   Plan: Free tier
   ```
4. คลิก "Create new project"

### 2.2 รับ Connection String
1. ไปที่ Settings > Database
2. ในส่วน Connection String เลือก "URI"
3. Copy connection string:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
   ```
4. เพิ่ม SSL mode:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
   ```

### 2.3 สร้าง Database Schema
1. ไปที่ SQL Editor ใน Supabase
2. รัน SQL script นี้:

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Status table
CREATE TABLE IF NOT EXISTS user_status (
    user_id VARCHAR PRIMARY KEY,
    display_name VARCHAR,
    picture_url VARCHAR,
    is_in_live_chat BOOLEAN DEFAULT FALSE,
    chat_mode VARCHAR DEFAULT 'manual',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat Messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR,
    sender_type VARCHAR,
    message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Form Submissions table
CREATE TABLE IF NOT EXISTS form_submissions (
    id VARCHAR PRIMARY KEY,
    form_type VARCHAR NOT NULL,
    user_id VARCHAR,
    user_name VARCHAR NOT NULL,
    user_email VARCHAR,
    user_phone VARCHAR,
    status VARCHAR DEFAULT 'pending',
    form_data TEXT,
    notes TEXT,
    assigned_to VARCHAR,
    priority INTEGER DEFAULT 1,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_user_status_user_id ON user_status(user_id);
CREATE INDEX idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at DESC);
CREATE INDEX idx_form_submissions_status ON form_submissions(status);
CREATE INDEX idx_form_submissions_form_type ON form_submissions(form_type);

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_status_updated_at BEFORE UPDATE
    ON user_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_form_submissions_updated_at BEFORE UPDATE
    ON form_submissions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## 3. 🔧 ปรับปรุงโค้ดสำหรับ Vercel

### 3.1 สร้าง vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "includeFiles": "templates/**"
    }
  }
}
```

### 3.2 สร้าง api/index.py
```python
# api/index.py
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the FastAPI app
from app.main import app

# Export for Vercel
app = app
```

### 3.3 อัพเดท requirements.txt สำหรับ Vercel
```txt
# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
httpx==0.25.2
python-dotenv==1.0.0

# Database
sqlalchemy[asyncio]==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Templates and static files
jinja2==3.1.2
python-multipart==0.0.6
aiofiles==23.2.1

# LINE Bot SDK
line-bot-sdk>=3.16.3

# Google Gemini AI
google-generativeai==0.3.2

# Utils
pytz==2023.3
pandas>=2.2.0
openpyxl==3.1.2

# Remove gunicorn as Vercel doesn't need it
```

### 3.4 สร้าง .env.production
```env
# Database (Supabase)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE=postgresql
ENVIRONMENT=production

# LINE Bot
LINE_CHANNEL_SECRET=your_line_channel_secret
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token

# Google Gemini
GEMINI_API_KEY=your_gemini_api_key

# Application
APP_TITLE=LINE Chatbot Admin System
APP_VERSION=2.9.4
SECRET_KEY=your-secret-key-here

# CORS (update with your Vercel domain)
CORS_ORIGINS=["https://your-app.vercel.app"]
```

## 4. 📦 การ Deploy บน Vercel

### 4.1 Push โค้ดไป GitHub
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 4.2 Import Project บน Vercel
1. Login ที่ https://vercel.com
2. คลิก "New Project"
3. Import Git Repository
4. เลือก repository ของคุณ
5. คลิก "Import"

### 4.3 ตั้งค่า Environment Variables
ใน Project Settings > Environment Variables:

```
DATABASE_URL = postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE = postgresql
ENVIRONMENT = production

LINE_CHANNEL_SECRET = your_actual_secret
LINE_CHANNEL_ACCESS_TOKEN = your_actual_token

GEMINI_API_KEY = your_actual_key

SECRET_KEY = generate-with-openssl-rand-hex-32
```

### 4.4 Deploy
1. คลิก "Deploy"
2. รอประมาณ 2-5 นาที
3. ตรวจสอบ deployment logs

## 5. 🔗 ตั้งค่า LINE Webhook

### 5.1 อัพเดท Webhook URL
1. ไปที่ LINE Developers Console
2. เลือก Channel ของคุณ
3. ในส่วน Messaging API:
   ```
   Webhook URL: https://your-app.vercel.app/webhook
   Use webhook: เปิด
   ```
4. คลิก "Verify" เพื่อทดสอบ

### 5.2 ทดสอบระบบ
1. เพิ่มบอทเป็นเพื่อน
2. ส่งข้อความทดสอบ
3. ตรวจสอบที่ Admin Panel: https://your-app.vercel.app/admin

## 6. 🐛 Troubleshooting

### 6.1 ปัญหาที่พบบ่อย

#### Database Connection Error
```python
# ตรวจสอบ DATABASE_URL format
# ต้องเป็น postgresql+asyncpg:// สำหรับ async operations
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
```

#### Static Files Not Loading
```javascript
// ใน vercel.json เพิ่ม
"functions": {
  "api/index.py": {
    "includeFiles": "static/**,templates/**"
  }
}
```

#### WebSocket Issues
```python
# Vercel ไม่รองรับ WebSocket แบบเต็มรูปแบบ
# ใช้ Server-Sent Events หรือ Polling แทน
```

### 6.2 Performance Optimization

#### 1. Database Connection Pooling
```python
# ใน database_config.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=5,  # ลดขนาด pool สำหรับ serverless
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300  # recycle every 5 minutes
)
```

#### 2. Cold Start Optimization
```python
# Preload models and configurations
from app.db.models import Base
from app.core.config import settings

# Initialize on import
settings.validate_required_settings()
```

## 7. 📊 Monitoring และ Maintenance

### 7.1 Vercel Analytics
- เปิด Analytics ใน Vercel Dashboard
- Monitor API response times
- Track error rates

### 7.2 Supabase Monitoring
- ใช้ Supabase Dashboard ดู:
  - Database size
  - Query performance
  - Connection count

### 7.3 Backup Strategy
```sql
-- Automated backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

## 8. 🚀 Production Checklist

- [ ] Environment variables ตั้งค่าครบถ้วน
- [ ] Database migrations รันเรียบร้อย
- [ ] LINE Webhook verified
- [ ] Admin panel accessible
- [ ] Test messages working
- [ ] Error handling configured
- [ ] Monitoring enabled
- [ ] Backup plan ready

## 9. 📱 URLs สำหรับทดสอบ

หลังจาก deploy เสร็จ:
- Main App: `https://your-app.vercel.app/`
- Admin Panel: `https://your-app.vercel.app/admin`
- API Docs: `https://your-app.vercel.app/docs`
- Health Check: `https://your-app.vercel.app/health`
- Dashboard: `https://your-app.vercel.app/ui/dashboard`

## 10. 💡 Tips & Best Practices

1. **Security**
   - ใช้ environment variables เสมอ
   - Enable RLS ใน Supabase
   - Validate input data

2. **Performance**
   - Implement caching where possible
   - Use database indexes
   - Optimize queries

3. **Scalability**
   - Monitor usage limits
   - Plan for growth
   - Consider paid plans when needed

---

🎉 **ยินดีด้วย! LINE Chatbot ของคุณพร้อมใช้งานบน Vercel + Supabase แล้ว!**

หากมีปัญหาหรือคำถาม สามารถตรวจสอบ:
- Vercel Logs
- Supabase Logs
- Browser Console
- Network Tab

Last Updated: ${new Date().toISOString()}
