# 📖 คู่มือการติดตั้งและใช้งาน LINE Bot Admin Panel

## 🚀 การติดตั้ง

### ขั้นตอนที่ 1: สำรองไฟล์เดิม
```bash
# เข้าไปยังโฟลเดอร์โปรเจกต์
cd /path/to/your/linebot/project

# สำรองไฟล์ admin.html เดิม
cp admin.html admin_backup_$(date +%Y%m%d_%H%M%S).html
```

### ขั้นตอนที่ 2: แทนที่ไฟล์ใหม่
```bash
# แทนที่ด้วยไฟล์ที่ปรับปรุงแล้ว
cp admin_final_complete.html admin.html
```

### ขั้นตอนที่ 3: เพิ่มไฟล์ Avatar (ถ้าต้องการ)
```bash
# สร้างโฟลเดอร์สำหรับ assets
mkdir -p static/images/avatars

# คัดลอกไฟล์ avatar
cp default_user_avatar.png static/images/avatars/
cp default_admin_avatar.png static/images/avatars/
cp default_bot_avatar.png static/images/avatars/
```

### ขั้นตอนที่ 4: ปรับปรุง Backend (ถ้าจำเป็น)

#### เพิ่ม File Upload Endpoint
```python
# เพิ่มใน main.py หรือ admin.py
from fastapi import UploadFile, File
from typing import List

@app.post("/admin/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    uploaded_files = []
    for file in files:
        # บันทึกไฟล์
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        uploaded_files.append({"filename": file.filename, "path": file_path})
    return {"files": uploaded_files}
```

#### เพิ่ม Message Actions Endpoints
```python
# เพิ่ม endpoints สำหรับ edit และ delete messages
@app.put("/admin/message/{message_id}")
async def edit_message(message_id: int, message_data: dict):
    # Logic สำหรับแก้ไขข้อความ
    pass

@app.delete("/admin/message/{message_id}")
async def delete_message(message_id: int):
    # Logic สำหรับลบข้อความ
    pass
```

## 🎯 การใช้งาน

### 1. การเข้าใช้งาน
- เปิดเบราว์เซอร์และไปที่ `/admin`
- ระบบจะแสดง Admin Panel ใหม่ที่ปรับปรุงแล้ว

### 2. การใช้งานบนเดสก์ท็อป

#### การนำทาง
- **Sidebar**: แสดงรายชื่อผู้ใช้ทั้งหมด
- **Chat Area**: พื้นที่แสดงการสนทนา
- **Input Area**: พื้นที่พิมพ์ข้อความ

#### คีย์ลัด
- `Ctrl + B`: เปิด/ปิด Sidebar
- `Ctrl + F`: ค้นหาผู้ใช้
- `Ctrl + D`: สลับ Dark/Light Mode
- `Ctrl + T`: เปิดเมนูธีม
- `Ctrl + E`: ส่งออกแชท
- `Ctrl + ;`: เปิด Emoji Picker
- `?`: แสดงคีย์ลัดทั้งหมด

#### การเปลี่ยนธีม
1. คลิกไอคอน palette ที่ header
2. เลือกธีมที่ต้องการ (Light, Dark, Blue, Green, Purple)
3. ธีมจะถูกบันทึกอัตโนมัติ

### 3. การใช้งานบนมือถือ

#### การนำทาง
- **Bottom Navigation**: แท็บด้านล่างสำหรับนำทาง
- **Swipe Gestures**: ปัดเพื่อเปิด/ปิด sidebar
- **Touch-friendly**: ปุ่มขนาดใหญ่เหมาะสำหรับการสัมผัส

#### การใช้งาน Sidebar
- ปัดจากขอบซ้ายเพื่อเปิด sidebar
- ปัดซ้ายหรือแตะพื้นหลังเพื่อปิด sidebar
- แตะชื่อผู้ใช้เพื่อเริ่มการสนทนา

### 4. ฟีเจอร์ต่างๆ

#### การค้นหาข้อความ
1. พิมพ์ในช่องค้นหาที่ sidebar
2. ระบบจะแสดงผลลัพธ์ทันที
3. คลิกผลลัพธ์เพื่อไปยังข้อความนั้น

#### การส่งไฟล์
1. คลิกไอคอน paperclip ในพื้นที่พิมพ์ข้อความ
2. เลือกไฟล์ที่ต้องการส่ง
3. ระบบจะแสดงตัวอย่างไฟล์
4. คลิกส่งเพื่อส่งไฟล์

#### การใช้ Emoji
1. คลิกไอคอน smile ในพื้นที่พิมพ์ข้อความ
2. เลือก emoji ที่ต้องการ
3. Emoji จะถูกแทรกลงในข้อความ

#### การส่งออกแชท
1. เลือกผู้ใช้ที่ต้องการส่งออกแชท
2. คลิกไอคอน settings ที่ header
3. คลิก "ส่งออกแชท"
4. ไฟล์ .txt จะถูกดาวน์โหลดอัตโนมัติ

#### การตั้งค่าการแจ้งเตือน
1. คลิกไอคอน settings ที่ header
2. เปิด/ปิด Desktop Notifications
3. เปิด/ปิด Sound Notifications
4. การตั้งค่าจะถูกบันทึกอัตโนมัติ

## 🔧 การแก้ไขปัญหา

### ปัญหาที่อาจพบ

#### 1. ธีมไม่เปลี่ยน
**สาเหตุ**: Local Storage ถูกบล็อก
**วิธีแก้**: 
- ตรวจสอบการตั้งค่าเบราว์เซอร์
- อนุญาต Local Storage สำหรับเว็บไซต์

#### 2. Notification ไม่ทำงาน
**สาเหตุ**: ไม่ได้อนุญาต notification permission
**วิธีแก้**:
- คลิกไอคอน lock ที่ address bar
- อนุญาต notifications

#### 3. เสียงแจ้งเตือนไม่เล่น
**สาเหตุ**: เบราว์เซอร์บล็อกการเล่นเสียงอัตโนมัติ
**วิธีแก้**:
- คลิกที่หน้าเว็บก่อนใช้งาน
- อนุญาต autoplay ในการตั้งค่าเบราว์เซอร์

#### 4. File Upload ไม่ทำงาน
**สาเหตุ**: Backend ยังไม่รองรับ
**วิธีแก้**:
- เพิ่ม endpoint สำหรับ file upload ที่ backend
- ตรวจสอบการตั้งค่า CORS

#### 5. Mobile Layout ผิดเพี้ยน
**สาเหตุ**: เบราว์เซอร์ไม่รองรับ CSS ใหม่
**วิธีแก้**:
- อัปเดตเบราว์เซอร์เป็นเวอร์ชันล่าสุด
- ใช้ Chrome หรือ Safari บนมือถือ

### การตรวจสอบ Console
เปิด Developer Tools (F12) และตรวจสอบ Console สำหรับ error messages

## 🔒 ความปลอดภัย

### 1. File Upload Security
- ตรวจสอบประเภทไฟล์ที่อนุญาต
- จำกัดขนาดไฟล์
- Scan ไฟล์หา malware

### 2. XSS Protection
- Sanitize user input
- ใช้ Content Security Policy (CSP)

### 3. CSRF Protection
- ใช้ CSRF tokens
- ตรวจสอบ origin headers

## 📊 การติดตามประสิทธิภาพ

### 1. Performance Monitoring
- ตรวจสอบ loading time
- Monitor memory usage
- ติดตาม network requests

### 2. User Analytics
- ติดตามการใช้งานฟีเจอร์ต่างๆ
- วิเคราะห์ user behavior
- Collect feedback

## 🆙 การอัปเดต

### การอัปเดตในอนาคต
1. สำรองไฟล์ปัจจุบัน
2. ทดสอบเวอร์ชันใหม่ใน staging environment
3. Deploy เมื่อทดสอบผ่านแล้ว
4. Monitor หลัง deployment

### Version Control
แนะนำให้ใช้ Git สำหรับ version control:
```bash
git add admin.html
git commit -m "Update admin panel with new UI/UX features"
git push origin main
```

## 📞 การขอความช่วยเหลือ

หากพบปัญหาหรือต้องการความช่วยเหลือ:
1. ตรวจสอบ Console errors
2. ดูเอกสารนี้อีกครั้ง
3. ตรวจสอบ browser compatibility
4. ติดต่อทีมพัฒนาพร้อมข้อมูล error logs

---

**หมายเหตุ**: คู่มือนี้ครอบคลุมการใช้งานพื้นฐาน สำหรับการปรับแต่งขั้นสูงกรุณาศึกษาโค้ดเพิ่มเติม

