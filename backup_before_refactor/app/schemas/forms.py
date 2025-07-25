# app/schemas/forms.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# === Enums ===
class FormType(str, Enum):
    KP7 = "kp7"
    ID_CARD = "id_card"

class FormStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    REJECTED = "rejected"

class PersonnelType(str, Enum):
    GOVERNMENT_OFFICER = "government_officer"  # ข้าราชการ
    GOVERNMENT_EMPLOYEE = "government_employee"  # พนักงานราชการ
    PERMANENT_EMPLOYEE = "permanent_employee"  # ลูกจ้างประจำ
    TEMPORARY_EMPLOYEE = "temporary_employee"  # ลูกจ้างชั่วคราว

class AdminRole(str, Enum):
    ADMIN = "admin"
    OFFICER = "officer"
    VIEWER = "viewer"

# === Form Schemas ===
class FormSubmissionBase(BaseModel):
    form_type: FormType
    user_name: str = Field(..., min_length=1, max_length=255)
    user_email: Optional[str] = Field(None, max_length=255)
    user_phone: Optional[str] = Field(None, max_length=20)
    form_data: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

class FormSubmissionCreate(FormSubmissionBase):
    pass

class FormSubmissionUpdate(BaseModel):
    status: Optional[FormStatus] = None
    notes: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)

class FormSubmission(FormSubmissionBase):
    id: str
    status: FormStatus
    priority: int
    assigned_to: Optional[str]
    submitted_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# === KP7 Specific Schemas ===
class KP7FormData(BaseModel):
    personnel_type: PersonnelType
    purpose: str = Field(..., min_length=1)  # วัตถุประสงค์
    position: Optional[str] = None  # ตำแหน่ง
    department: Optional[str] = None  # หน่วยงาน
    education_level: Optional[str] = None  # ระดับการศึกษา
    requested_documents: List[str] = Field(default_factory=list)

# === ID Card Specific Schemas ===
class IDCardFormData(BaseModel):
    card_type: str = Field(..., min_length=1)  # ประเภทบัตร
    reason: str = Field(..., min_length=1)  # เหตุผล
    photo_appointment: Optional[datetime] = None  # นัดหมายถ่ายรูป
    delivery_method: Optional[str] = None  # วิธีการรับบัตร

# === Admin User Schemas ===
class AdminUserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    role: AdminRole = AdminRole.OFFICER

class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=8)

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    role: Optional[AdminRole] = None
    is_active: Optional[bool] = None

class AdminUser(AdminUserBase):
    id: str
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# === File Attachment Schemas ===
class FileAttachmentBase(BaseModel):
    file_name: str = Field(..., min_length=1, max_length=255)
    file_size: Optional[int] = Field(None, ge=0)
    mime_type: Optional[str] = Field(None, max_length=100)

class FileAttachmentCreate(FileAttachmentBase):
    form_id: str
    file_path: str

class FileAttachment(FileAttachmentBase):
    id: str
    form_id: str
    file_path: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

# === Response Schemas ===
class FormListResponse(BaseModel):
    forms: List[FormSubmission]
    total: int
    page: int
    per_page: int
    total_pages: int

class DashboardStats(BaseModel):
    total_today: int
    pending_count: int
    processing_count: int
    completed_count: int
    rejected_count: int
    average_processing_days: float
    
class ActivityLog(BaseModel):
    id: str
    action: str
    description: str
    user_name: str
    timestamp: datetime
    
class DashboardData(BaseModel):
    stats: DashboardStats
    recent_activities: List[ActivityLog]
    pending_forms: List[FormSubmission]
