# app/db/models.py
from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class UserStatus(Base):
    __tablename__ = "user_status"
    
    user_id = Column(String, primary_key=True, index=True)
    display_name = Column(String, nullable=True)  # เก็บชื่อผู้ใช้จาก LINE Profile
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
