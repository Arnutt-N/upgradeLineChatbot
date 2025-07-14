# คู่มือการพัฒนาและวิเคราะห์โค้ดด้วย Gemini CLI

เอกสารนี้เป็นการรวบรวมข้อมูลสำคัญสำหรับการพัฒนาและวิเคราะห์โค้ดในโปรเจกต์นี้ โดยครอบคลุมตั้งแต่คำสั่งพื้นฐานในการพัฒนา, ภาพรวมสถาปัตยกรรมของระบบ, ไปจนถึงการใช้เครื่องมือ AI อย่าง Gemini CLI เพื่อวิเคราะห์โค้ดเบสขนาดใหญ่

---

## การใช้ Gemini CLI เพื่อวิเคราะห์โค้ดเบสขนาดใหญ่

เมื่อต้องการวิเคราะห์โค้ดเบสขนาดใหญ่หรือไฟล์จำนวนมากที่อาจเกินขีดจำกัดของ Context Window ทั่วไป การใช้ Gemini CLI จะเป็นเครื่องมือที่มีประสิทธิภาพสูง เนื่องจากมี Context Window ที่ใหญ่มาก ใช้คำสั่ง `gemini -p` เพื่อดึงความสามารถนี้มาใช้งาน

### Syntax การระบุไฟล์และไดเรกทอรี

คุณสามารถแนบไฟล์และไดเรกทอรีใน prompt ของ Gemini ได้โดยใช้ `@` syntax โดยระบุ path แบบ relative จากตำแหน่งที่คุณรันคำสั่ง `gemini`

### **ตัวอย่าง**

* **วิเคราะห์ไฟล์เดียว:**
    ```bash
    gemini -p "@src/main.py อธิบายวัตถุประสงค์และโครงสร้างของไฟล์นี้"
    ```
* **วิเคราะห์หลายไฟล์:**
    ```bash
    gemini -p "@package.json @src/index.js วิเคราะห์ dependencies ที่ใช้ในโค้ด"
    ```
* **วิเคราะห์ทั้งไดเรกทอรี:**
    ```bash
    gemini -p "@src/ สรุปสถาปัตยกรรมของโค้ดเบสนี้"
    ```
* **วิเคราะห์หลายไดเรกทอรี:**
    ```bash
    gemini -p "@src/ @tests/ วิเคราะห์ test coverage สำหรับ source code"
    ```
* **วิเคราะห์ไดเรกทอรีปัจจุบันและไดเรกทอรีย่อยทั้งหมด:**
    ```bash
    gemini -p "@./ ให้ภาพรวมของโปรเจกต์นี้ทั้งหมด"
    ```
* **หรือใช้ flag `--all_files`:**
    ```bash
    gemini --all_files -p "วิเคราะห์โครงสร้างโปรเจกต์และ dependencies"
    ```

### **ตัวอย่างการตรวจสอบการ Implement**

นี่คือตัวอย่างการใช้ Gemini CLI เพื่อตรวจสอบการ implement ฟีเจอร์ต่างๆ ในโค้ดเบสนี้:

* **ตรวจสอบว่าฟีเจอร์ถูก implement แล้วหรือไม่:**
    ```bash
    gemini -p "@src/ @lib/ ฟีเจอร์ dark mode ถูก implement ในโค้ดเบสนี้แล้วหรือยัง? แสดงไฟล์และฟังก์ชันที่เกี่ยวข้อง"
    ```
* **ตรวจสอบการ implement ระบบยืนยันตัวตน:**
    ```bash
    gemini -p "@src/ @middleware/ มีการ implement JWT authentication หรือไม่? แสดงรายการ endpoint และ middleware ทั้งหมดที่เกี่ยวกับ auth"
    ```
* **ตรวจสอบ pattern ที่เฉพาะเจาะจง:**
    ```bash
    gemini -p "@src/ มี React hooks ที่จัดการ WebSocket connections หรือไม่? แสดงรายการพร้อม path ของไฟล์"
    ```
* **ตรวจสอบการจัดการ error:**
    ```bash
    gemini -p "@src/ @api/ มีการ implement error handling ที่เหมาะสมสำหรับ API endpoints ทั้งหมดหรือไม่? แสดงตัวอย่างของ try-catch blocks"
    ```
* **ตรวจสอบการทำ rate limiting:**
    ```bash
    gemini -p "@backend/ @middleware/ มีการ implement rate limiting สำหรับ API หรือไม่? แสดงรายละเอียดการ implement"
    ```
* **ตรวจสอบกลยุทธ์การ caching:**
    ```bash
    gemini -p "@src/ @lib/ @services/ มีการ implement Redis caching หรือไม่? แสดงรายการฟังก์ชันที่เกี่ยวกับ cache และการใช้งานทั้งหมด"
    ```
* **ตรวจสอบมาตรการความปลอดภัยที่เฉพาะเจาะจง:**
    ```bash
    gemini -p "@src/ @api/ มีการป้องกัน SQL injection หรือไม่? แสดงวิธีการ sanitize user inputs"
    ```
* **ตรวจสอบ test coverage สำหรับฟีเจอร์:**
    ```bash
    gemini -p "@src/payment/ @tests/ โมดูลประมวลผลการชำระเงินได้รับการทดสอบครบถ้วนหรือไม่? แสดงรายการ test cases ทั้งหมด"
    ```

### **ควรใช้ Gemini CLI เมื่อใด**

* เมื่อต้องการวิเคราะห์โค้ดเบสทั้งหมดหรือไดเรกทอรีขนาดใหญ่
* เมื่อต้องการเปรียบเทียบไฟล์ขนาดใหญ่หลายๆ ไฟล์
* เมื่อต้องการทำความเข้าใจ pattern หรือสถาปัตยกรรมในภาพรวมของโปรเจกต์
* เมื่อ Context Window ของเครื่องมืออื่นไม่เพียงพอต่องาน
* เมื่อทำงานกับไฟล์ที่มีขนาดรวมกันมากกว่า 100KB
* เมื่อต้องการตรวจสอบว่าฟีเจอร์, pattern, หรือมาตรการความปลอดภัยที่เฉพาะเจาะจงได้ถูก implement แล้วหรือไม่
* เมื่อต้องการตรวจสอบการมีอยู่ของ coding pattern บางอย่างทั่วทั้งโค้ดเบส

### **ข้อควรจำ**

* Path ที่ใช้กับ `@` syntax จะเป็นแบบ relative เทียบกับ working directory ปัจจุบันที่คุณรันคำสั่ง `gemini`
* CLI จะแนบเนื้อหาของไฟล์เข้าไปใน context โดยตรง
* Gemini มี Context Window ขนาดใหญ่ที่สามารถรองรับโค้ดเบสทั้งโปรเจกต์ซึ่งอาจทำให้โมเดลอื่น ๆ มีปัญหาได้
* ในการตรวจสอบการ implement ควรระบุสิ่งที่ต้องการค้นหาให้ชัดเจนและเฉพาะเจาะจงเพื่อให้ได้ผลลัพธ์ที่แม่นยำ

---

## ภาพรวมการพัฒนาและโปรเจกต์

ส่วนนี้ให้รายละเอียดเกี่ยวกับคำสั่งในการพัฒนา, สถาปัตยกรรม, และรายละเอียดการ implement ที่สำคัญของโปรเจกต์นี้

### คำสั่งในการพัฒนา (Development Commands)

#### **การรันแอปพลิเคชัน**

* **Development server พร้อม auto-reload:**
    ```bash
    python app/main.py
    ```
* **Production server:**
    ```bash
    uvicorn app.main:app --host 0.0.0.0 --port 8000
    ```
* **รันผ่าน Docker:**
    ```bash
    docker-compose up --build
    ```

#### **การจัดการฐานข้อมูล**

* **รัน database migration:**
    ```bash
    python run_migration.py
    ```
* **ตรวจสอบสถานะฐานข้อมูล:**
    ```bash
    python check_database.py
    ```
* **สำรองข้อมูลฐานข้อมูล:**
    ```bash
    python create_sample_data.py
    ```
* **ทดสอบการเชื่อมต่อฐานข้อมูล:**
    ```bash
    python test_db.py
    ```
* **Backfill ข้อมูลรูปโปรไฟล์:**
    ```bash
    python backfill_avatars_simple.py
    ```

#### **การทดสอบและตรวจสอบความถูกต้อง**

* **รันชุดทดสอบทั้งหมด:**
    ```bash
    python test_enhanced_system.py
    ```
* **ทดสอบระบบรูปโปรไฟล์:**
    ```bash
    python test_avatar_system.py
    ```
* **ตรวจสอบข้อมูลผู้ใช้:**
    ```bash
    python check_users.py
    ```
* **ทดสอบการปรับปรุง UI:**
    ```bash
    python test_ui_enhancement.py
    ```

#### **Batch Operations (สำหรับ Windows)**

มีไฟล์ `.bat` สำหรับการทำงานที่รวดเร็ว ดังนี้:

* `run_test.bat`: ทดสอบการ migration ฐานข้อมูล
* `run_migration.bat`: รันการ migration ฐานข้อมูล
* `run_backfill.bat`: รันการ backfill รูปโปรไฟล์
* `run_check_users.bat`: ตรวจสอบสถานะผู้ใช้

---

## ภาพรวมสถาปัตยกรรม (Architecture Overview)

### โครงสร้างหลักของแอปพลิเคชัน

นี่คือแอปพลิเคชัน LINE Bot ที่พัฒนาด้วย FastAPI พร้อมกับหน้าแอดมินสองระบบ

**ส่วนประกอบหลัก:**

* **การเชื่อมต่อ LINE Bot**: ระบบแชทแบบเรียลไทม์พร้อมการจัดการ webhook
* **ระบบแอดมินสองส่วน**:
    * `/admin` - หน้า Live chat สำหรับการสนทนาใน LINE Bot
    * `/form-admin` - ระบบจัดการฟอร์มสำหรับคำขอ KP7 และบัตรประชาชน
* **ระบบวิเคราะห์ข้อมูลขั้นสูง**: Dashboard พร้อมข้อมูลและกราฟแบบเรียลไทม์
* **การเชื่อมต่อ Telegram**: ระบบแจ้งเตือนสำหรับแอดมิน

### สถาปัตยกรรมฐานข้อมูล

**ตารางหลัก:**

* `user_status` - โปรไฟล์ผู้ใช้ LINE พร้อม URL รูปโปรไฟล์และชื่อที่แสดง
* `chat_messages` - ประวัติการแชทพร้อมข้อความจากแอดมิน/ผู้ใช้/บอท
* `form_submissions` - คำขอฟอร์ม (KP7, บัตรประชาชน) พร้อมสถานะของ workflow
* **ตารางสำหรับ Tracking ขั้นสูง** (5 ตารางใหม่):
    * `chat_history` - ข้อมูลวิเคราะห์การแชทอย่างละเอียด
    * `friend_activities` - การติดตามการ follow/unfollow
    * `telegram_notifications` - คิวและสถานะการแจ้งเตือน
    * `system_logs` - การบันทึก Log และการ monitor ระบบ
    * `settings` - การตั้งค่าแบบไดนามิก

### สถาปัตยกรรม Service Layer

**Services หลัก:**

* `line_handler_enhanced.py` - การประมวลผล LINE webhook ขั้นสูงพร้อมการดึงข้อมูลโปรไฟล์
* `telegram_service.py` - การจัดการคิวและการส่งการแจ้งเตือน
* `history_service.py` - การรวบรวมและรายงานข้อมูลวิเคราะห์
* `ws_manager.py` - การเชื่อมต่อ WebSocket สำหรับการอัปเดตหน้าแอดมินแบบเรียลไทม์

### โครงสร้าง API Router

* `webhook.py` - Endpoints สำหรับ LINE Bot webhook
* `admin.py` - หน้าแอดมินสำหรับ Live chat
* `form_admin.py` - การจัดการฟอร์มพร้อมระบบยืนยันตัวตน
* `enhanced_api.py` - API สำหรับข้อมูลวิเคราะห์พร้อมข้อมูลจำลอง (mock data) เป็น fallback
* `ui_router.py` - การให้บริการไฟล์ template สำหรับ frontend

---

## รายละเอียดการ Implement ที่สำคัญ

### รูปแบบการเชื่อมต่อฐานข้อมูล

แอปพลิเคชันใช้ async SQLAlchemy พร้อมกับการสร้างฐานข้อมูลและตารางโดยอัตโนมัติเมื่อเริ่มต้น การดำเนินการกับฐานข้อมูลทั้งหมดใช้ Dependency Injection ผ่าน `get_db()` เพื่อการจัดการ session ที่เหมาะสม

### Flow การทำงานของ LINE Handler ขั้นสูง

1.  **การดึงข้อมูลโปรไฟล์ (Profile Enrichment)**: ทุกข้อความจะกระตุ้นการดึงข้อมูลโปรไฟล์พร้อมระบบ fallback รูปโปรไฟล์ 3 ระดับ
2.  **การ Tracking สองชั้น (Dual Tracking)**: ข้อความจะถูกบันทึกลงทั้งในตาราง `chat_messages` เดิมและตาราง `chat_history` ใหม่
3.  **กิจกรรมเพื่อน (Friend Activity)**: การ follow/unfollow จะถูกติดตามในตาราง `friend_activities`
4.  **การแจ้งเตือนผ่าน Telegram**: การกระทำของแอดมินจะกระตุ้นการแจ้งเตือนผ่านระบบคิว

### กลยุทธ์ Fallback ของ API

Endpoints สำหรับข้อมูลวิเคราะห์ทั้งหมดมีการ implement fallback ไปยังข้อมูลจำลอง (mock data) เมื่อ service หลักล้มเหลว เพื่อให้แน่ใจว่า UI จะไม่พัง รูปแบบจะเป็นดังนี้:

```python
try:
    real_data = await service.get_data()
    return real_data
except Exception:
    return mock_data