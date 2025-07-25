# Static Files Test Instructions

## การทดสอบ Static Files หลัง Phase 4

### 🚀 เริ่มเซิร์ฟเวอร์
```bash
cd D:\hrProject\upgradeLineChatbot
python main.py
```

### 🧪 ทดสอบ Endpoints

#### 1. Test Static API Endpoint
```
GET http://localhost:8000/test-static
```
Response ควรมี URLs สำหรับทดสอบ

#### 2. Test Avatar Files
```
GET http://localhost:8000/static/images/avatars/default_user_avatar.png
GET http://localhost:8000/static/images/avatars/default_admin_avatar.png
GET http://localhost:8000/static/images/avatars/default_bot_avatar.png
```
ควรเห็นรูป Avatar

#### 3. Test HTML Page
```
GET http://localhost:8000/static/test.html
```
ควรเห็นหน้าทดสอบพร้อมรูป Avatar ทั้ง 3

### ✅ ผลลัพธ์ที่คาดหวัง

1. **API Endpoint**: JSON response พร้อม static URLs
2. **Avatar Images**: รูป PNG แสดงผลถูกต้อง
3. **Test Page**: หน้า HTML พร้อมรูป Avatar
4. **No 404 Errors**: ไม่มี error 404 Not Found

### ❌ การแก้ไขปัญหา

หากมี Error:
1. ตรวจสอบโฟลเดอร์ static/ มีอยู่จริง
2. ตรวจสอบไฟล์ Avatar อยู่ใน static/images/avatars/
3. ตรวจสอบ import StaticFiles ใน app/main.py
4. ตรวจสอบ dependency aiofiles ติดตั้งแล้ว

### 📋 Checklist

- [ ] Server เริ่มต้นได้โดยไม่มี error
- [ ] /test-static ส่ง JSON response
- [ ] รูป Avatar แสดงผลได้
- [ ] test.html แสดงหน้าเว็บได้
- [ ] ไม่มี 404 errors
