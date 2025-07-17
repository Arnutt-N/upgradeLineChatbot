# 🚀 Vercel + Supabase Deployment Checklist

## Pre-Deployment Checklist

### 1. Supabase Setup ✅
- [ ] สร้าง Supabase account
- [ ] สร้าง project ใหม่ (region: Singapore)
- [ ] Copy DATABASE_URL พร้อม password
- [ ] เพิ่ม ?sslmode=require ต่อท้าย URL
- [ ] รัน SQL schema creation script

### 2. Environment Variables ✅
สร้าง `.env.production` พร้อมค่าต่อไปนี้:
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres?sslmode=require
DB_TYPE=postgresql
ENVIRONMENT=production
LINE_CHANNEL_SECRET=xxx
LINE_CHANNEL_ACCESS_TOKEN=xxx
GEMINI_API_KEY=xxx
SECRET_KEY=xxx
```

### 3. Code Preparation ✅
- [ ] สร้าง `vercel.json` (ตรวจสอบแล้ว ✓)
- [ ] สร้าง `api/index.py` (ตรวจสอบแล้ว ✓)
- [ ] อัพเดท `requirements.txt` ให้เหมาะกับ Vercel
- [ ] ทดสอบ migration script locally

### 4. Data Migration (Optional) ✅
```bash
# รัน migration script
cd vercel_deployment
python migrate_to_supabase.py
```

### 5. Git Push ✅
```bash
git add .
git commit -m "feat: Add Vercel deployment configuration"
git push origin main
```

## Deployment Steps

### 1. Vercel Deployment
1. Login ที่ https://vercel.com
2. New Project > Import Git Repository
3. เลือก repository ของคุณ
4. Environment Variables:
   - คลิก "Environment Variables"
   - เพิ่มทุกค่าจาก `.env.production`
5. คลิก "Deploy"

### 2. Post-Deployment
- [ ] ตรวจสอบ deployment logs
- [ ] ทดสอบ endpoints:
  - `https://[your-app].vercel.app/health`
  - `https://[your-app].vercel.app/admin`
- [ ] อัพเดท LINE webhook URL
- [ ] ทดสอบส่งข้อความผ่าน LINE

### 3. Monitoring
- [ ] เปิด Vercel Analytics
- [ ] ตั้งค่า error alerts
- [ ] Monitor Supabase usage

## Quick Commands

### Test Connection
```python
python vercel_deployment/migrate_to_supabase.py
```

### Local Testing with Production DB
```bash
# สร้าง .env.local จาก .env.production
cp .env.production .env.local
# รัน locally
python main.py
```

### Force Redeploy
```bash
git commit --allow-empty -m "force redeploy"
git push origin main
```

## Troubleshooting

### Common Issues:
1. **Module not found**: ตรวจสอบ PYTHONPATH ใน vercel.json
2. **Database connection failed**: ตรวจสอบ DATABASE_URL และ SSL mode
3. **Static files 404**: ตรวจสอบ includeFiles ใน vercel.json
4. **Webhook timeout**: ตรวจสอบ maxDuration setting

### Debug Commands:
```bash
# Check Vercel logs
vercel logs [deployment-url]

# Test locally with production env
vercel dev
```

## Success Indicators ✅
- Health endpoint returns 200
- Admin panel loads correctly
- LINE webhook verified
- Messages flow correctly
- No errors in Vercel logs

---
Last Updated: ${new Date().toISOString()}
