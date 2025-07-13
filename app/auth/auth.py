# app/auth/auth.py
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.models import AdminUser

# Simple session storage (in production, use Redis or database)
active_sessions = {}

security = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    """Hash password using SHA256 with salt"""
    salt = "forms_admin_salt_2025"  # In production, use random salt per user
    return hashlib.sha256((password + salt).encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def create_session_token() -> str:
    """Create secure session token"""
    return secrets.token_urlsafe(32)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[AdminUser]:
    """Authenticate admin user"""
    from app.db.crud_forms import get_admin_user_by_username
    
    user = await get_admin_user_by_username(db, username)
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    # For demo purposes, accept both hashed and plain passwords
    if user.password_hash == "$2b$12$dummy_hash_for_demo":
        # Demo account - accept simple passwords
        if password in ["admin", "officer", "123456"]:
            return user
    else:
        # Real password verification
        if verify_password(password, user.password_hash):
            return user
    
    return None

def create_access_token(user: AdminUser) -> str:
    """Create access token for user"""
    token = create_session_token()
    expires_at = datetime.now() + timedelta(hours=8)  # 8 hour session
    
    active_sessions[token] = {
        "user_id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "role": user.role,
        "expires_at": expires_at
    }
    
    return token

async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    """Get current authenticated user"""
    
    # Try to get token from Authorization header
    token = None
    if credentials:
        token = credentials.credentials
    
    # Try to get token from session cookie
    if not token:
        token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if token exists and is valid
    session_data = active_sessions.get(token)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if session is expired
    if datetime.now() > session_data["expires_at"]:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    from app.db.crud_forms import get_admin_user_by_username
    user = await get_admin_user_by_username(db, session_data["username"])
    
    if not user or not user.is_active:
        del active_sessions[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def logout_user(token: str) -> bool:
    """Logout user by removing session"""
    if token in active_sessions:
        del active_sessions[token]
        return True
    return False

def require_admin(user: AdminUser = Depends(get_current_user)):
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

def get_session_info() -> dict:
    """Get current session information (for debugging)"""
    active_count = len(active_sessions)
    sessions = []
    
    for token, data in active_sessions.items():
        sessions.append({
            "username": data["username"],
            "role": data["role"],
            "expires_at": data["expires_at"].isoformat(),
            "token_preview": token[:8] + "..."
        })
    
    return {
        "active_sessions": active_count,
        "sessions": sessions
    }
