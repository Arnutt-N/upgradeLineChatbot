# PostgreSQL-specific models for AI Agent น้อง HR Moj
from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class UserStatus(Base):
    """ข้อมูลผู้ใช้ LINE พร้อม PostgreSQL features"""
    __tablename__ = "user_status"
    
    # ใช้ UUID แทน String ID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    is_in_live_chat = Column(Boolean, default=False)
    chat_mode = Column(String(20), default='manual')
    display_name = Column(Text)
    picture_url = Column(Text)
    
    # PostgreSQL JSONB สำหรับ metadata
    user_metadata = Column(JSONB, default={})
    preferences = Column(JSONB, default={})
    
    # Timestamps with timezone
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_created', created_at),
        Index('idx_user_metadata', user_metadata, postgresql_using='gin'),
    )

class ChatMessage(Base):
    """ประวัติการแชทพร้อม Full-text search"""
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(50), ForeignKey('user_status.user_id'), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False)  # 'user', 'bot', 'admin'
    message = Column(Text, nullable=False)
    
    # JSONB for rich message data
    message_data = Column(JSONB, default={})
    attachments = Column(JSONB, default=[])
    
    # Session tracking
    session_id = Column(String(100), index=True)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    # PostgreSQL Full-text search for Thai language
    __table_args__ = (
        Index('idx_message_fulltext', 
              func.to_tsvector('simple', message),
              postgresql_using='gin'),
        Index('idx_message_created', created_at),
        Index('idx_session_user', session_id, user_id),
    )

class FormSubmission(Base):
    """คำขอฟอร์มต่างๆ พร้อม JSONB storage"""
    __tablename__ = "form_submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    form_type = Column(String(50), nullable=False, index=True)  # 'kp7', 'id_card'
    user_id = Column(String(50), ForeignKey('user_status.user_id'), index=True)
    
    # User information
    user_name = Column(String(200), nullable=False)
    user_email = Column(String(200))
    user_phone = Column(String(20))
    
    # Status tracking
    status = Column(String(20), default='pending', index=True)
    priority = Column(Integer, default=1)
    
    # JSONB for flexible form data
    form_data = Column(JSONB, nullable=False)
    notes = Column(JSONB, default=[])
    history = Column(JSONB, default=[])
    
    # Assignment
    assigned_to = Column(String(100))
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Performance indexes
    __table_args__ = (
        Index('idx_form_status_type', status, form_type),
        Index('idx_form_data', form_data, postgresql_using='gin'),
        Index('idx_form_submitted', submitted_at),
    )

class AnalyticsEvent(Base):
    """การเก็บ Analytics events แบบ Time-series"""
    __tablename__ = "analytics_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(String(50), index=True)
    
    # JSONB for flexible event data
    event_data = Column(JSONB, nullable=False)
    
    # Time-series optimization
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    
    # Partitioning by month (PostgreSQL feature)
    __table_args__ = (
        Index('idx_event_time_type', created_at, event_type),
        Index('idx_event_data', event_data, postgresql_using='gin'),
    )

class SystemSettings(Base):
    """การตั้งค่าระบบแบบ Key-Value"""
    __tablename__ = "system_settings"
    
    key = Column(String(100), primary_key=True)
    value = Column(JSONB, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String(100))

# Function to create all tables
def create_tables(engine):
    """Create all PostgreSQL tables with proper settings"""
    Base.metadata.create_all(engine)
    
    # Create additional PostgreSQL-specific objects
    with engine.connect() as conn:
        # Create text search configuration for Thai
        conn.execute("""
            CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS thai (COPY = simple);
        """)
        
        # Create function for updated_at trigger
        conn.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ language 'plpgsql';
        """)
