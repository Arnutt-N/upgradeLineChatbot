# Quick Start: PostgreSQL + Supabase + Render

## 🚀 ขั้นตอนด่วน (15 นาที)

### 1️⃣ Supabase (5 นาที)
1. ไปที่ https://supabase.com → New project
2. ตั้งชื่อ + password → Create project
3. Settings → Database → Connection string → Copy

### 2️⃣ เตรียมโปรเจค (5 นาที)
```bash
# 1. Clone และเข้าโฟลเดอร์
git clone https://github.com/your-repo/upgradeLineChatbot.git
cd upgradeLineChatbot

# 2. สร้าง .env จาก template
cp .env.postgres.example .env

# 3. แก้ไข .env - ใส่ข้อมูลจริง
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE=postgresql
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx
GEMINI_API_KEY=xxx

# 4. ติดตั้ง dependencies
pip install -r requirements_postgres.txt

# 5. Migrate database
python migrate_to_postgresql.py
```

### 3️⃣ Deploy บน Render (5 นาที)
1. Push code ไป GitHub
2. ไปที่ https://render.com → New → Web Service
3. Connect GitHub repo → เลือก branch
4. ตั้งค่า:
   - **Build Command**: `pip install -r requirements_postgres.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Environment → Add:
   ```
   DATABASE_URL = [Supabase connection string]
   DB_TYPE = postgresql
   LINE_CHANNEL_SECRET = xxx
   LINE_CHANNEL_ACCESS_TOKEN = xxx
   GEMINI_API_KEY = xxx
   ```
6. Create Web Service → รอ deploy (~5 นาที)

## ✅ เช็คการทำงาน

### Test Endpoints:
- Health: `https://your-app.onrender.com/health`
- Admin: `https://your-app.onrender.com/admin`
- API Docs: `https://your-app.onrender.com/docs`

### LINE Webhook:
ตั้งค่าใน LINE Developers Console:
```
https://your-app.onrender.com/webhook
```

## 🔧 Troubleshooting

### Connection Error
```bash
# ตรวจสอบ connection string
python test_postgresql_connection.py
```

### Tables Not Found
```bash
# สร้าง tables ใหม่
python migrate_to_postgresql.py
```

### Performance Slow
- Upgrade Supabase plan (Free → Pro)
- หรือใช้ Render PostgreSQL ($7/month)

## 📊 Monitoring

### Supabase Dashboard
- Database → Query Editor
- Monitoring → Database Health

### Render Dashboard
- Logs → ดู real-time logs
- Metrics → CPU/Memory usage

---
🎉 เสร็จแล้ว! ระบบพร้อมใช้งานกับ PostgreSQL
