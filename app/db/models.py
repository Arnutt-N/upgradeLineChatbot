# app/db/models.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

# === Existing LINE Admin Models ===

class UserStatus(Base):
    __tablename__ = "user_status"
    
    user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)  # เก็บชื่อผู้ใช้จาก LINE Profile
    picture_url = Column(String, nullable=True)  # เก็บ URL รูปโปรไฟล์จาก LINE Profile
    is_in_live_chat = Column(Boolean, default=False)
    chat_mode = Column(String, default='manual')  # 'manual' หรือ 'auto'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    sender_type = Column(String)  # 'user', 'bot', 'admin'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# === New Forms System Models ===

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

# === New Enhanced Models ===

class ChatHistory(Base):
    """ตารางประวัติการแชทแบบละเอียด"""
    __tablename__ = "chat_history"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    message_type = Column(String, nullable=False, index=True)  # 'user', 'admin', 'bot'
    message_content = Column(Text, nullable=False)
    admin_user_id = Column(String, index=True)  # ถ้าเป็นการตอบจากแอดมิน
    is_read = Column(Boolean, default=False)
    message_id = Column(String, index=True)  # LINE message ID
    reply_token = Column(String)  # LINE reply token
    session_id = Column(String, index=True)  # Chat session grouping
    extra_data = Column(Text)  # JSON additional data (user agent, etc.)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class FriendActivity(Base):
    """ตารางประวัติการเพิ่มเพื่อน/บล็อค/ยกเลิกการติดตาม"""
    __tablename__ = "friend_activity"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    activity_type = Column(String, nullable=False, index=True)  # 'follow', 'unfollow', 'block', 'unblock'
    user_profile = Column(Text)  # JSON ข้อมูลโปรไฟล์ตอนนั้น
    source = Column(String, default='line_webhook')  # 'line_webhook', 'manual', 'import'
    event_data = Column(Text)  # JSON ข้อมูล event ดิบจาก LINE
    ip_address = Column(String)  # IP address ถ้ามี
    user_agent = Column(String)  # User agent ถ้ามี
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class TelegramNotification(Base):
    """ตารางการแจ้งเตือนไปยัง Telegram"""
    __tablename__ = "telegram_notifications"
    
    id = Column(String, primary_key=True, index=True)
    notification_type = Column(String, nullable=False, index=True)  # 'chat_request', 'new_friend', 'system_alert', 'user_message'
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    user_id = Column(String, index=True)  # LINE user ID ที่เกี่ยวข้อง
    telegram_message_id = Column(Integer, index=True)  # Message ID ที่ส่งไป Telegram
    telegram_chat_id = Column(String)  # Telegram chat ID ที่ส่งไป
    status = Column(String, default='pending', index=True)  # 'pending', 'sent', 'failed', 'retry'
    error_message = Column(Text)  # Error message ถ้าส่งไม่สำเร็จ
    retry_count = Column(Integer, default=0)
    retry_after = Column(DateTime(timezone=True))  # วันที่จะ retry ครั้งถัดไป
    priority = Column(Integer, default=1)  # ลำดับความสำคัญ 1-5 (5 = สูงสุด)
    extra_data = Column(Text)  # JSON additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    sent_at = Column(DateTime(timezone=True))  # วันที่ส่งสำเร็จ

class TelegramSettings(Base):
    """ตารางการตั้งค่า Telegram Bot"""
    __tablename__ = "telegram_settings"
    
    id = Column(String, primary_key=True, index=True)
    setting_key = Column(String, unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)  # JSON value
    setting_type = Column(String, default='string')  # 'string', 'number', 'boolean', 'json'
    description = Column(Text)
    category = Column(String, default='general')  # 'general', 'notifications', 'alerts', 'bot'
    is_sensitive = Column(Boolean, default=False)  # ถ้าเป็น sensitive data
    updated_by = Column(String)  # ใครแก้ไข
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemLogs(Base):
    """ตารางประวัติการทำงานของระบบ (แยกจาก audit logs)"""
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True, index=True)
    log_level = Column(String, nullable=False, index=True)  # 'debug', 'info', 'warning', 'error', 'critical'
    category = Column(String, nullable=False, index=True)  # 'line_webhook', 'telegram', 'admin', 'system', 'database'
    subcategory = Column(String, index=True)
    module = Column(String, index=True)  # ชื่อ module ที่เกิด log
    function_name = Column(String)  # ชื่อ function ที่เกิด log
    message = Column(Text, nullable=False)
    details = Column(Text)  # JSON additional data
    user_id = Column(String, index=True)  # LINE user ID ที่เกี่ยวข้อง (ถ้ามี)
    session_id = Column(String, index=True)  # Session ID (ถ้ามี)
    request_id = Column(String, index=True)  # Request ID สำหรับ tracking
    execution_time = Column(Integer)  # เวลาที่ใช้ในการทำงาน (milliseconds)
    memory_usage = Column(Integer)  # การใช้ memory (bytes)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

# === Shared System Models (ปรับปรุง) ===

class SharedNotification(Base):
    """ตารางแจ้งเตือนระหว่างระบบ"""
    __tablename__ = "shared_notifications"
    
    id = Column(String, primary_key=True, index=True)
    from_system = Column(String, nullable=False)  # 'forms' หรือ 'line_admin'
    to_system = Column(String, nullable=False)
    notification_type = Column(String, nullable=False)  # 'form_update', 'chat_alert'
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
