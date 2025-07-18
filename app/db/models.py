# app/db/models.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

Base = declarative_base()

# === Existing LINE Admin Models ===

class UserStatus(Base):
    __tablename__ = "user_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  # เพิ่ม id column
    user_id = Column(String, unique=True, nullable=False, index=True)  # ทำให้ unique
    display_name = Column(String, nullable=True)  # เก็บชื่อผู้ใช้จาก LINE Profile
    picture_url = Column(String, nullable=True)  # เก็บ URL รูปโปรไฟล์จาก LINE Profile
    is_in_live_chat = Column(Boolean, default=False)
    chat_mode = Column(String, default='manual')  # 'manual' หรือ 'auto'
    user_metadata = Column(Text, nullable=True)  # JSON metadata
    preferences = Column(Text, nullable=True)  # JSON preferences
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    sender_type = Column(String)  # 'user', 'bot', 'admin'
    message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChatHistory(Base):
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    message_type = Column(String, nullable=False)  # 'user_message', 'bot_response', 'admin_message'
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    message_id = Column(String, nullable=True)  # LINE message ID
    is_processed = Column(Boolean, default=True)

# === Additional Models for Complete System ===

class FriendActivity(Base):
    __tablename__ = "friend_activity"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    activity_type = Column(String, nullable=False)  # 'added', 'removed', 'blocked'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    details = Column(Text, nullable=True)

class SystemLogs(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String, nullable=False)  # 'info', 'warning', 'error'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String, nullable=True)
    additional_data = Column(Text, nullable=True)  # JSON
