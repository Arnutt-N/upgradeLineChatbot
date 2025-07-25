# app/schemas/chat.py
from pydantic import BaseModel

class ReplyPayload(BaseModel):
    user_id: str
    message: str

class EndChatPayload(BaseModel):
    user_id: str

class ToggleModePayload(BaseModel):
    user_id: str
    mode: str  # 'manual' หรือ 'auto'

class WebSocketMessage(BaseModel):
    type: str
    userId: str
    message: str
