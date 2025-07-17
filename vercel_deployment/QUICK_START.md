# 🚀 Vercel Quick Start (ฉบับย่อ)

## 1️⃣ สมัคร Vercel
1. ไปที่ https://vercel.com
2. Sign up ด้วย GitHub (ง่ายสุด)
3. Authorize Vercel

## 2️⃣ Push Code ไป GitHub
```bash
cd D:\hrProject\upgradeLineChatbot
git add .
git commit -m "Ready for Vercel"
git push origin main
```

## 3️⃣ Import Project
1. ที่ Vercel คลิก "Add New" > "Project"
2. เลือก repository `line-chatbot`
3. คลิก "Import"

## 4️⃣ ตั้ง Environment Variables
เพิ่มค่าเหล่านี้:
- `DATABASE_URL` = [Supabase PostgreSQL URL]
- `DB_TYPE` = postgresql
- `ENVIRONMENT` = production
- `LINE_CHANNEL_SECRET` = [จาก LINE]
- `LINE_CHANNEL_ACCESS_TOKEN` = [จาก LINE]
- `GEMINI_API_KEY` = [จาก Google]
- `SECRET_KEY` = [generate ด้วย openssl]

## 5️⃣ Deploy
1. คลิก "Deploy"
2. รอ 2-5 นาที
3. เสร็จ! 🎉

## 6️⃣ Update LINE Webhook
1. LINE Developers Console
2. Webhook URL: `https://your-app.vercel.app/webhook`
3. Verify & Enable

## 📱 Test URLs
- Homepage: `https://your-app.vercel.app/`
- Admin: `https://your-app.vercel.app/admin`
- Health: `https://your-app.vercel.app/health`

## 🔧 ถ้ามีปัญหา
1. ดู Build Logs
2. ตรวจสอบ Environment Variables
3. Check Vercel Functions Logs

---
✨ **Deploy อัตโนมัติทุกครั้งที่ push code!**
