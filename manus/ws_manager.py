# app/services/ws_manager.py
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """เชื่อมต่อ WebSocket ใหม่"""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """ตัดการเชื่อมต่อ WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """ส่งข้อความไปยัง WebSocket เฉพาะ"""
        await websocket.send_text(message)

    async def broadcast(self, data: dict):
        """ส่งข้อความไปยัง WebSocket ทั้งหมด"""
        message = json.dumps(data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                # ลบ connection ที่มีปัญหา
                if connection in self.active_connections:
                    self.active_connections.remove(connection)

# สร้าง instance สำหรับใช้งาน
manager = ConnectionManager()
