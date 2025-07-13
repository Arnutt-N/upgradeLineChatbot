# app/db/crud_forms.py
import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload

from app.db.models import FormSubmission, FormAttachment, AdminUser, FormStatusHistory
from app.schemas.forms import (
    FormSubmissionCreate, FormSubmissionUpdate, 
    AdminUserCreate, AdminUserUpdate,
    FormStatus, FormType
)

# === Form Submission CRUD ===

async def create_form_submission(
    db: AsyncSession, 
    form_data: FormSubmissionCreate
) -> FormSubmission:
    """สร้างคำขอฟอร์มใหม่"""
    form_id = str(uuid.uuid4())
    
    db_form = FormSubmission(
        id=form_id,
        form_type=form_data.form_type.value,
        user_name=form_data.user_name,
        user_email=form_data.user_email,
        user_phone=form_data.user_phone,
        form_data=json.dumps(form_data.form_data, ensure_ascii=False),
        notes=form_data.notes,
        status='pending',
        priority=1
    )
    
    db.add(db_form)
    await db.commit()
    await db.refresh(db_form)
    
    # เพิ่มประวัติสถานะ
    await create_status_history(db, form_id, None, 'pending', None, "สร้างคำขอใหม่")
    
    return db_form

async def get_form_submission(db: AsyncSession, form_id: str) -> Optional[FormSubmission]:
    """ดึงข้อมูลคำขอฟอร์มตาม ID"""
    result = await db.execute(
        select(FormSubmission)
        .options(selectinload(FormSubmission.attachments))
        .options(selectinload(FormSubmission.status_history))
        .where(FormSubmission.id == form_id)
    )
    return result.scalar_one_or_none()

async def get_form_submissions(
    db: AsyncSession,
    form_type: Optional[FormType] = None,
    status: Optional[FormStatus] = None,
    assigned_to: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[FormSubmission]:
    """ดึงรายการคำขอฟอร์ม"""
    query = select(FormSubmission).options(selectinload(FormSubmission.attachments))
    
    # กรองตามเงื่อนไข
    if form_type:
        query = query.where(FormSubmission.form_type == form_type.value)
    if status:
        query = query.where(FormSubmission.status == status.value)
    if assigned_to:
        query = query.where(FormSubmission.assigned_to == assigned_to)
    
    # เรียงลำดับ
    query = query.order_by(desc(FormSubmission.submitted_at))
    query = query.limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_form_submission(
    db: AsyncSession,
    form_id: str,
    form_update: FormSubmissionUpdate,
    updated_by: Optional[str] = None
) -> Optional[FormSubmission]:
    """อัพเดทคำขอฟอร์ม"""
    db_form = await get_form_submission(db, form_id)
    if not db_form:
        return None
    
    old_status = db_form.status
    
    # อัพเดทข้อมูล
    if form_update.status:
        db_form.status = form_update.status.value
    if form_update.notes is not None:
        db_form.notes = form_update.notes
    if form_update.assigned_to is not None:
        db_form.assigned_to = form_update.assigned_to
    if form_update.priority is not None:
        db_form.priority = form_update.priority
    
    db_form.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_form)
    
    # บันทึกประวัติการเปลี่ยนสถานะ
    if form_update.status and old_status != form_update.status.value:
        await create_status_history(
            db, form_id, old_status, form_update.status.value, 
            updated_by, form_update.notes
        )
    
    return db_form

async def delete_form_submission(db: AsyncSession, form_id: str) -> bool:
    """ลบคำขอฟอร์ม"""
    db_form = await get_form_submission(db, form_id)
    if not db_form:
        return False
    
    await db.delete(db_form)
    await db.commit()
    return True

# === Form Statistics ===

async def get_dashboard_stats(db: AsyncSession) -> Dict[str, Any]:
    """ดึงสถิติสำหรับ Dashboard"""
    today = datetime.now().date()
    
    # คำขอวันนี้
    today_count_result = await db.execute(
        select(func.count(FormSubmission.id))
        .where(func.date(FormSubmission.submitted_at) == today)
    )
    today_count = today_count_result.scalar() or 0
    
    # นับตามสถานะ
    status_counts = {}
    for status in ['pending', 'processing', 'completed', 'rejected']:
        result = await db.execute(
            select(func.count(FormSubmission.id))
            .where(FormSubmission.status == status)
        )
        status_counts[status] = result.scalar() or 0
    
    # คำขอทั้งหมด
    total_result = await db.execute(select(func.count(FormSubmission.id)))
    total_count = total_result.scalar() or 0
    
    return {
        "total_today": today_count,
        "pending_count": status_counts.get('pending', 0),
        "processing_count": status_counts.get('processing', 0),
        "completed_count": status_counts.get('completed', 0),
        "rejected_count": status_counts.get('rejected', 0),
        "total_count": total_count,
        "average_processing_days": 0.0  # TODO: คำนวณจริง
    }

# === Status History ===

async def create_status_history(
    db: AsyncSession,
    form_id: str,
    old_status: Optional[str],
    new_status: str,
    changed_by: Optional[str],
    notes: Optional[str] = None
) -> FormStatusHistory:
    """สร้างประวัติการเปลี่ยนสถานะ"""
    history = FormStatusHistory(
        id=str(uuid.uuid4()),
        form_id=form_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        notes=notes
    )
    
    db.add(history)
    await db.commit()
    await db.refresh(history)
    return history

# === Admin User CRUD ===

async def create_admin_user(
    db: AsyncSession,
    user_data: AdminUserCreate,
    password_hash: str
) -> AdminUser:
    """สร้างผู้ดูแลระบบใหม่"""
    db_user = AdminUser(
        id=str(uuid.uuid4()),
        username=user_data.username,
        password_hash=password_hash,
        full_name=user_data.full_name,
        email=user_data.email,
        role=user_data.role.value
    )
    
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_admin_user_by_username(db: AsyncSession, username: str) -> Optional[AdminUser]:
    """ดึงข้อมูลผู้ดูแลระบบตาม username"""
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == username)
    )
    return result.scalar_one_or_none()

async def get_admin_users(
    db: AsyncSession,
    is_active: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> List[AdminUser]:
    """ดึงรายการผู้ดูแลระบบ"""
    query = select(AdminUser)
    
    if is_active is not None:
        query = query.where(AdminUser.is_active == is_active)
    
    query = query.order_by(AdminUser.created_at).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return result.scalars().all()
