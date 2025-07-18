# app/db/models.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

# === Core LINE Admin Models ===

class UserStatus(Base):
    __tablename__ = "user_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, nullable=False, index=True)
    display_name = Column(String, nullable=True)
    picture_url = Column(String, nullable=True)
    is_in_live_chat = Column(Boolean, default=False)
    chat_mode = Column(String, default='manual')
    user_metadata = Column(Text, nullable=True)
    preferences = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    sender_type = Column(String)
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    message_type = Column(String, nullable=False)
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    message_id = Column(String, nullable=True)
    is_processed = Column(Boolean, default=True)

# === Activity and Logging Models ===

class FriendActivity(Base):
    __tablename__ = "friend_activity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    activity_type = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

class SystemLogs(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, nullable=True)
    additional_data = Column(Text, nullable=True)

# === Telegram Integration Models ===

class TelegramNotification(Base):
    __tablename__ = "telegram_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    telegram_message_id = Column(String, nullable=True)
    status = Column(String, default='pending')

class TelegramSettings(Base):
    __tablename__ = "telegram_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String, unique=True, nullable=False)
    setting_value = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# === Forms System Models ===

class FormSubmission(Base):
    __tablename__ = "form_submissions"
    
    id = Column(String, primary_key=True, index=True)
    form_type = Column(String, nullable=False, index=True)
    user_id = Column(String, index=True)
    user_name = Column(String, nullable=False)
    user_email = Column(String)
    user_phone = Column(String)
    status = Column(String, default='pending', index=True)
    form_data = Column(Text)
    notes = Column(Text)
    assigned_to = Column(String, index=True)
    priority = Column(Integer, default=1)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    attachments = relationship("FormAttachment", back_populates="form", cascade="all, delete-orphan")
    status_history = relationship("FormStatusHistory", back_populates="form", cascade="all, delete-orphan")

class FormAttachment(Base):
    __tablename__ = "form_attachments"
    
    id = Column(String, primary_key=True, index=True)
    form_id = Column(String, ForeignKey("form_submissions.id"), nullable=False, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    form = relationship("FormSubmission", back_populates="attachments")

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String)
    role = Column(String, default='officer')
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FormStatusHistory(Base):
    __tablename__ = "form_status_history"
    
    id = Column(String, primary_key=True, index=True)
    form_id = Column(String, ForeignKey("form_submissions.id"), nullable=False, index=True)
    old_status = Column(String)
    new_status = Column(String, nullable=False)
    changed_by = Column(String)
    notes = Column(Text)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    form = relationship("FormSubmission", back_populates="status_history")

# === Shared Notification Models ===

class SharedNotification(Base):
    __tablename__ = "shared_notifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    notification_type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)

class SharedAuditLog(Base):
    __tablename__ = "shared_audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource_type = Column(String, nullable=False)
    resource_id = Column(String, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String, nullable=True)
