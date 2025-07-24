# app/services/ws_manager.py
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
import json
from datetime import datetime

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
        """ส่งข้อความไปยัง WebSocket ทั้งหมด with enhanced error handling"""
        if not self.active_connections:
            print("No active WebSocket connections to broadcast to")
            return
            
        message = json.dumps(data, ensure_ascii=False, default=str)
        print(f"Broadcasting to {len(self.active_connections)} connections: {data.get('type', 'unknown')}")
        
        # Keep track of broken connections to remove them
        broken_connections = []
        
        for connection in self.active_connections[:]:  # Create a copy to iterate safely
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                broken_connections.append(connection)
        
        # Remove broken connections
        for broken_conn in broken_connections:
            if broken_conn in self.active_connections:
                self.active_connections.remove(broken_conn)
                
        if broken_connections:
            print(f"Removed {len(broken_connections)} broken connections. Active: {len(self.active_connections)}")
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.active_connections)
    
    async def broadcast_system_status(self, status: dict):
        """Broadcast system status to all connections"""
        await self.broadcast({
            "type": "system_status",
            "timestamp": datetime.now().isoformat(),
            **status
        })

# สร้าง instance สำหรับใช้งาน
manager = ConnectionManager()
