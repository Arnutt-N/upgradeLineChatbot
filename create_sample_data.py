#!/usr/bin/env python3
"""
Sample Data Creator for Forms Admin System
Phase 3: Development
"""

import asyncio
import sys
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from app.db.database import get_db, AsyncSessionLocal
from app.db.models import FormSubmission, AdminUser, FormStatusHistory
from sqlalchemy import text

async def create_sample_admin_users():
    """สร้างผู้ดูแลระบบตัวอย่าง"""
    print("Creating sample admin users...")
    
    async with AsyncSessionLocal() as db:
        # Admin หลัก
        admin_user = AdminUser(
            id=str(uuid.uuid4()),
            username="admin",
            password_hash="$2b$12$dummy_hash_for_demo",  # ในการใช้จริงต้องเป็น bcrypt hash
            full_name="ผู้ดูแลระบบหลัก",
            email="admin@forms.local",
            role="admin",
            is_active=True,
            created_at=datetime.now()
        )
        db.add(admin_user)
        
        # เจ้าหน้าที่
        officer_user = AdminUser(
            id=str(uuid.uuid4()),
            username="officer",
            password_hash="$2b$12$dummy_hash_for_demo",
            full_name="เจ้าหน้าที่ประมวลผล",
            email="officer@forms.local",
            role="officer",
            is_active=True,
            created_at=datetime.now()
        )
        db.add(officer_user)
        
        await db.commit()
        print("✅ Created 2 admin users")
        return admin_user.id, officer_user.id

async def create_sample_forms(admin_id, officer_id):
    """สร้างคำขอฟอร์มตัวอย่าง"""
    print("Creating sample form submissions...")
    
    async with AsyncSessionLocal() as db:
        forms_data = [
            # KP7 Forms
            {
                "id": str(uuid.uuid4()),
                "form_type": "kp7",
                "user_name": "นาย สมชาย ใจดี",
                "user_email": "somchai@email.com",
                "user_phone": "081-234-5678",
                "status": "pending",
                "form_data": json.dumps({
                    "personnel_type": "government_officer",
                    "purpose": "ปรับวิทยะฐานะ",
                    "position": "นักวิชาการศึกษา",
                    "department": "กรมการฝึกหัดครู",
                    "education_level": "ปริญญาโท",
                    "requested_documents": ["ประวัติการศึกษา", "ประวัติการทำงาน"]
                }, ensure_ascii=False),
                "notes": "คำขอปกติ รอการตรวจสอบ",
                "priority": 2,
                "submitted_at": datetime.now() - timedelta(hours=2)
            },
            {
                "id": str(uuid.uuid4()),
                "form_type": "kp7",
                "user_name": "นาง สมหญิง ใจงาม",
                "user_email": "somying@email.com",
                "user_phone": "082-345-6789",
                "status": "processing",
                "form_data": json.dumps({
                    "personnel_type": "government_employee",
                    "purpose": "ลาออก",
                    "position": "เจ้าหน้าที่บริหารงานทั่วไป",
                    "department": "สำนักงานเขตพื้นที่การศึกษา",
                    "requested_documents": ["ประวัติการทำงาน", "การลา"]
                }, ensure_ascii=False),
                "notes": "กำลังตรวจสอบเอกสาร",
                "assigned_to": officer_id,
                "priority": 1,
                "submitted_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": str(uuid.uuid4()),
                "form_type": "kp7",
                "user_name": "นาย สมศักดิ์ ใจใส",
                "user_email": "somsak@email.com",
                "user_phone": "083-456-7890",
                "status": "completed",
                "form_data": json.dumps({
                    "personnel_type": "permanent_employee",
                    "purpose": "ปรับวิทยะฐานะ",
                    "position": "ลูกจ้างประจำ",
                    "department": "โรงเรียนประถมศึกษา",
                    "requested_documents": ["ประวัติการศึกษา"]
                }, ensure_ascii=False),
                "notes": "ดำเนินการเสร็จสิ้น ส่งเอกสารแล้ว",
                "assigned_to": admin_id,
                "priority": 3,
                "submitted_at": datetime.now() - timedelta(days=3),
                "updated_at": datetime.now() - timedelta(hours=6)
            },
            # ID Card Forms
            {
                "id": str(uuid.uuid4()),
                "form_type": "id_card",
                "user_name": "นาย วิชัย มั่นใจ",
                "user_email": "wichai@email.com",
                "user_phone": "084-567-8901",
                "status": "pending",
                "form_data": json.dumps({
                    "card_type": "บัตรประจำตัวข้าราชการ",
                    "reason": "ทำใหม่ (หาบบัตรเก่า)",
                    "photo_appointment": None,
                    "delivery_method": "รับที่สำนักงาน"
                }, ensure_ascii=False),
                "notes": "รอนัดหมายถ่ายรูป",
                "priority": 2,
                "submitted_at": datetime.now() - timedelta(hours=5)
            },
            {
                "id": str(uuid.uuid4()),
                "form_type": "id_card",
                "user_name": "นาง ประดิษฐ์ สร้างสรรค์",
                "user_email": "pradit@email.com",
                "user_phone": "085-678-9012",
                "status": "processing",
                "form_data": json.dumps({
                    "card_type": "บัตรประจำตัวพนักงานราชการ",
                    "reason": "ต่ออายุ",
                    "photo_appointment": (datetime.now() + timedelta(days=2)).isoformat(),
                    "delivery_method": "ส่งทางไปรษณีย์"
                }, ensure_ascii=False),
                "notes": "นัดถ่ายรูปแล้ว รอมาถ่าย",
                "assigned_to": officer_id,
                "priority": 1,
                "submitted_at": datetime.now() - timedelta(days=2)
            }
        ]
        
        for form_data in forms_data:
            form = FormSubmission(**form_data)
            db.add(form)
        
        await db.commit()
        print(f"✅ Created {len(forms_data)} sample forms")
        return [form["id"] for form in forms_data]

async def create_sample_status_history(form_ids, admin_id, officer_id):
    """สร้างประวัติสถานะตัวอย่าง"""
    print("Creating sample status history...")
    
    async with AsyncSessionLocal() as db:
        history_data = [
            # Form 1 - pending
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[0],
                "old_status": None,
                "new_status": "pending",
                "changed_by": None,
                "notes": "สร้างคำขอใหม่",
                "changed_at": datetime.now() - timedelta(hours=2)
            },
            # Form 2 - pending -> processing
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[1],
                "old_status": None,
                "new_status": "pending",
                "changed_by": None,
                "notes": "สร้างคำขอใหม่",
                "changed_at": datetime.now() - timedelta(days=1)
            },
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[1],
                "old_status": "pending",
                "new_status": "processing",
                "changed_by": officer_id,
                "notes": "เริ่มตรวจสอบเอกสาร",
                "changed_at": datetime.now() - timedelta(hours=12)
            },
            # Form 3 - pending -> processing -> completed
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[2],
                "old_status": None,
                "new_status": "pending",
                "changed_by": None,
                "notes": "สร้างคำขอใหม่",
                "changed_at": datetime.now() - timedelta(days=3)
            },
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[2],
                "old_status": "pending",
                "new_status": "processing",
                "changed_by": admin_id,
                "notes": "เริ่มดำเนินการ",
                "changed_at": datetime.now() - timedelta(days=2)
            },
            {
                "id": str(uuid.uuid4()),
                "form_id": form_ids[2],
                "old_status": "processing",
                "new_status": "completed",
                "changed_by": admin_id,
                "notes": "ดำเนินการเสร็จสิ้น ส่งเอกสารแล้ว",
                "changed_at": datetime.now() - timedelta(hours=6)
            }
        ]
        
        for history in history_data:
            status_history = FormStatusHistory(**history)
            db.add(status_history)
        
        await db.commit()
        print(f"✅ Created {len(history_data)} status history records")

async def main():
    """Main function"""
    print("=" * 50)
    print("FORMS ADMIN SAMPLE DATA CREATOR")
    print("Phase 3: Development")
    print("=" * 50)
    
    try:
        # Create admin users
        admin_id, officer_id = await create_sample_admin_users()
        
        # Create sample forms
        form_ids = await create_sample_forms(admin_id, officer_id)
        
        # Create status history
        await create_sample_status_history(form_ids, admin_id, officer_id)
        
        print("\n✅ Sample Data Creation Summary:")
        print("  - Admin users: 2")
        print("  - Form submissions: 5")
        print("  - Status history: 6")
        print("\nForms Admin system is ready with sample data!")
        
    except Exception as e:
        print(f"\nError creating sample data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
