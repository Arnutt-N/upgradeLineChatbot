# app/schemas/auth.py
from pydantic import BaseModel
from typing import Optional

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    user_info: dict
    message: str

class UserInfo(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    is_active: bool

class SessionInfo(BaseModel):
    active_sessions: int
    current_user: Optional[UserInfo] = None
