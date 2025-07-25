# app/db/models_forms.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.models import Base  # ใช้ Base เดียวกัน

# === Forms System Models ===

class FormSubmission(Base):
    """ตารางหลักสำหรับคำขอฟอร์มทั้งหมด"""
    __tablename__ = "form_submissions"
    
    id = Column(String, primary_key=True, index=True)
    form_type = Column(String, nullable=False, index=True)  # 'kp7', 'id_card'
    user_id = Column(String, index=True)  # Link to user_status (optional)
    user_name = Column(String, nullable=False)
    user_email = Column(String)
    user_phone = Column(String)
    status = Column(String, default='pending', index=True)  # pending, processing, completed, rejected
    form_data = Column(Text)  # JSON ข้อมูลฟอร์ม
    notes = Column(Text)  # หมายเหตุ
    assigned_to = Column(String, index=True)  # เจ้าหน้าที่ที่รับผิดชอบ
    priority = Column(Integer, default=1)  # ลำดับความสำคัญ 1-5
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attachments = relationship("FormAttachment", back_populates="form", cascade="all, delete-orphan")
    status_history = relationship("FormStatusHistory", back_populates="form", cascade="all, delete-orphan")

class FormAttachment(Base):
    """ตารางไฟล์แนบของฟอร์ม"""
    __tablename__ = "form_attachments"
    
    id = Column(String, primary_key=True, index=True)
    form_id = Column(String, ForeignKey("form_submissions.id"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    form = relationship("FormSubmission", back_populates="attachments")

class AdminUser(Base):
    """ตารางผู้ดูแลระบบฟอร์ม"""
    __tablename__ = "admin_users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String)
    role = Column(String, default='officer')  # admin, officer, viewer
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FormStatusHistory(Base):
    """ตารางประวัติการเปลี่ยนสถานะฟอร์ม"""
    __tablename__ = "form_status_history"
    
    id = Column(String, primary_key=True, index=True)
    form_id = Column(String, ForeignKey("form_submissions.id"), nullable=False, index=True)
    old_status = Column(String)
    new_status = Column(String, nullable=False)
    changed_by = Column(String)  # admin_user_id
    notes = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    form = relationship("FormSubmission", back_populates="status_history")

# === Shared System Models ===

class SharedNotification(Base):
    """ตารางแจ้งเตือนระหว่างระบบ"""
    __tablename__ = "shared_notifications"
    
    id = Column(String, primary_key=True, index=True)
    from_system = Column(String, nullable=False)  # 'forms' หรือ 'line_admin'
    to_system = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'form_update', 'chat_alert'
    data = Column(Text)  # JSON data
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SharedAuditLog(Base):
    """ตารางบันทึกการทำงานของระบบ"""
    __tablename__ = "shared_audit_logs"
    
    id = Column(String, primary_key=True, index=True)
    system = Column(String, nullable=False)  # 'forms' หรือ 'line_admin'
    action = Column(String, nullable=False)  # 'create', 'update', 'delete'
    table_name = Column(String)
    record_id = Column(String)
    user_id = Column(String)
    changes = Column(Text)  # JSON before/after
    created_at = Column(DateTime(timezone=True), server_default=func.now())
