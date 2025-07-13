#!/usr/bin/env python3
import asyncio
import sqlite3
import json
import uuid
from datetime import datetime, timedelta

def create_sample_forms():
    """Create sample form data directly with sqlite3"""
    conn = sqlite3.connect("chatbot.db")
    cursor = conn.cursor()
    
    print("Creating sample form submissions...")
    
    # Sample forms data
    forms = [
        (
            str(uuid.uuid4()),
            "kp7",
            None,
            "นาย สมชาย ใจดี",
            "somchai@email.com",
            "081-234-5678",
            "pending",
            json.dumps({"purpose": "ปรับวิทยะฐานะ", "position": "นักวิชาการศึกษา"}),
            "คำขอปกติ รอการตรวจสอบ",
            None,
            2,
            (datetime.now() - timedelta(hours=2)).isoformat(),
            None
        ),
        (
            str(uuid.uuid4()),
            "kp7", 
            None,
            "นาง สมหญิง ใจงาม",
            "somying@email.com",
            "082-345-6789",
            "processing",
            json.dumps({"purpose": "ลาออก", "position": "เจ้าหน้าที่บริหารงานทั่วไป"}),
            "กำลังตรวจสอบเอกสาร",
            "82faf8a2-d3f6-41f8-9f67-cca96f010415",
            1,
            (datetime.now() - timedelta(days=1)).isoformat(),
            None
        ),
        (
            str(uuid.uuid4()),
            "kp7",
            None,
            "นาย สมศักดิ์ ใจใส",
            "somsak@email.com", 
            "083-456-7890",
            "completed",
            json.dumps({"purpose": "ปรับวิทยะฐานะ", "position": "ลูกจ้างประจำ"}),
            "ดำเนินการเสร็จสิ้น ส่งเอกสารแล้ว",
            "86b67df2-c3ed-4fa7-8f2f-3f855c42e966",
            3,
            (datetime.now() - timedelta(days=3)).isoformat(),
            (datetime.now() - timedelta(hours=6)).isoformat()
        ),
        (
            str(uuid.uuid4()),
            "id_card",
            None,
            "นาย วิชัย มั่นใจ",
            "wichai@email.com",
            "084-567-8901", 
            "pending",
            json.dumps({"card_type": "บัตรประจำตัวข้าราชการ", "reason": "ทำใหม่"}),
            "รอนัดหมายถ่ายรูป",
            None,
            2,
            (datetime.now() - timedelta(hours=5)).isoformat(),
            None
        ),
        (
            str(uuid.uuid4()),
            "id_card",
            None,
            "นาง ประดิษฐ์ สร้างสรรค์",
            "pradit@email.com",
            "085-678-9012",
            "processing", 
            json.dumps({"card_type": "บัตรประจำตัวพนักงานราชการ", "reason": "ต่ออายุ"}),
            "นัดถ่ายรูปแล้ว รอมาถ่าย",
            "82faf8a2-d3f6-41f8-9f67-cca96f010415",
            1,
            (datetime.now() - timedelta(days=2)).isoformat(),
            None
        )
    ]
    
    # Insert forms
    cursor.executemany("""
        INSERT INTO form_submissions 
        (id, form_type, user_id, user_name, user_email, user_phone, status, 
         form_data, notes, assigned_to, priority, submitted_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, forms)
    
    conn.commit()
    print(f"Created {len(forms)} sample forms")
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM form_submissions")
    count = cursor.fetchone()[0]
    print(f"Total forms in database: {count}")
    
    conn.close()
    print("Sample data creation completed!")

if __name__ == "__main__":
    create_sample_forms()
