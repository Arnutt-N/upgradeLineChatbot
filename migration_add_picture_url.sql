-- migration_add_picture_url.sql
-- เพิ่ม picture_url column ลงใน user_status table
-- สร้างเมื่อ: 2025-07-10
-- วัตถุประสงค์: เพิ่มฟีเจอร์การจัดเก็บ URL รูปโปรไฟล์ผู้ใช้

-- ตรวจสอบ schema ปัจจุบัน
.schema user_status

-- เพิ่ม column picture_url (อนุญาตให้เป็น NULL)
ALTER TABLE user_status ADD COLUMN picture_url TEXT NULL;

-- ตรวจสอบ schema หลังจากเพิ่ม column
.schema user_status

-- แสดงข้อมูลตัวอย่าง
SELECT user_id, display_name, picture_url, is_in_live_chat FROM user_status LIMIT 5;

-- แสดงจำนวนผู้ใช้ทั้งหมด
SELECT COUNT(*) as total_users FROM user_status;
