# 🔧 Vercel Troubleshooting Guide

## ❌ ปัญหาที่พบบ่อยและวิธีแก้

### 1. Build Failed: Module Not Found
**Error**: `ModuleNotFoundError: No module named 'xxx'`

**สาเหตุ**: ขาด package ใน requirements.txt

**แก้ไข**:
```bash
# เพิ่ม package ที่ขาดใน requirements.txt
echo "package-name==version" >> requirements.txt
git add requirements.txt
git commit -m "Add missing package"
git push
```

---

### 2. Runtime Error: Python Version
**Error**: `Python version 3.x is not available`

**สาเหตุ**: Vercel ไม่รองรับ Python version นั้น

**แก้ไข**:
1. เพิ่มใน vercel.json:
```json
{
  "builds": [{
    "src": "api/index.py",
    "use": "@vercel/python",
    "config": {
      "runtime": "python3.11"
    }
  }]
}
```

---

### 3. Import Error: Parent Module
**Error**: `ImportError: attempted relative import with no known parent`

**สาเหตุ**: Path ไม่ถูกต้องใน serverless

**แก้ไข** ใน api/index.py:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

### 4. Database Connection Failed
**Error**: `asyncpg.exceptions.InvalidPasswordError`

**สาเหตุ**: Password มีอักขระพิเศษ หรือ URL format ผิด

**แก้ไข**:
1. Encode password ถ้ามีอักขระพิเศษ
2. ตรวจสอบ format:
```
postgresql://user:password@host:5432/database?sslmode=require
```

---

### 5. Template Not Found
**Error**: `TemplateNotFound: admin.html`

**สาเหตุ**: Vercel ไม่ include template files

**แก้ไข** ใน vercel.json:
```json
{
  "functions": {
    "api/index.py": {
      "includeFiles": "templates/**,app/templates/**"
    }
  }
}
```

---

### 6. Static Files 404
**Error**: Static files ไม่โหลด (CSS/JS/Images)

**สาเหตุ**: Route configuration ผิด

**แก้ไข** ใน vercel.json:
```json
{
  "routes": [
    {
      "src": "/static/(.*)",
      "dest": "/static/$1"
    }
  ]
}
```

---

### 7. Function Timeout
**Error**: `FUNCTION_INVOCATION_TIMEOUT`

**สาเหตุ**: Function ทำงานเกิน 10 วินาที

**แก้ไข**:
1. Optimize code ให้เร็วขึ้น
2. ใช้ background jobs สำหรับงานหนัก
3. Upgrade เป็น Pro plan (timeout 60s)

---

### 8. Environment Variable Not Found
**Error**: `KeyError: 'LINE_CHANNEL_SECRET'`

**สาเหตุ**: ไม่ได้ตั้ง environment variable

**แก้ไข**:
1. ไปที่ Project Settings > Environment Variables
2. เพิ่มตัวแปรที่ขาด
3. Redeploy

---

### 9. CORS Error
**Error**: `Access-Control-Allow-Origin`

**สาเหตุ**: CORS policy block

**แก้ไข** ใน FastAPI:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 10. Memory Limit Exceeded
**Error**: `Error: memory limit exceeded`

**สาเหตุ**: ใช้ memory เกิน 1GB

**แก้ไข**:
1. ลด memory usage
2. ใช้ streaming สำหรับไฟล์ใหญ่
3. Clear unused variables

---

## 🛠️ Debug Tools

### 1. ดู Real-time Logs
```bash
vercel logs your-app.vercel.app --follow
```

### 2. ทดสอบ Locally
```bash
vercel dev
```

### 3. Check Build Output
```bash
vercel inspect your-deployment-url
```

### 4. Environment Variables
```bash
vercel env pull .env.local
```

---

## 💡 Pro Tips

1. **Always check logs first** - ข้อมูลละเอียดอยู่ใน logs
2. **Test locally** - ใช้ `vercel dev` ทดสอบก่อน deploy
3. **Use GitHub Actions** - สำหรับ CI/CD ที่ซับซ้อน
4. **Monitor usage** - ดู bandwidth และ invocations
5. **Cache static assets** - ลด bandwidth usage

---

## 📞 ขอความช่วยเหลือ

1. **Vercel Discord**: https://vercel.com/discord
2. **GitHub Discussions**: เปิด discussion ใน repo
3. **Stack Overflow**: tag ด้วย `vercel`
4. **Official Docs**: https://vercel.com/docs

---

สู้ๆ ครับ! 💪 ปัญหาทุกอย่างมีทางแก้
