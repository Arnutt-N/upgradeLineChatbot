# Static Assets Directory

โฟลเดอร์นี้เก็บไฟล์ static assets สำหรับ LINE Bot Admin Panel

## โครงสร้าง

```
static/
├── css/          # ไฟล์ CSS (สำหรับอนาคต)
├── fonts/        # ไฟล์ฟอนต์ (สำหรับอนาคต)
├── images/       # รูปภาพต่างๆ
│   └── avatars/  # รูป Avatar เริ่มต้น
└── js/           # ไฟล์ JavaScript (สำหรับอนาคต)
```

## การใช้งาน

ไฟล์ในโฟลเดอร์นี้จะสามารถเข้าถึงได้ผ่าน URL:
- `http://localhost:8000/static/images/avatars/default_user_avatar.png`
- `https://your-domain.com/static/images/avatars/default_user_avatar.png`

## หมายเหตุ

- โฟลเดอร์ทั้งหมดพร้อมใช้งาน
- FastAPI StaticFiles middleware จะต้องถูกเพิ่มใน app/main.py
- ไฟล์ avatar จะถูกคัดลอกมาจากโฟลเดอร์ manus ใน Phase 3
