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
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """ตัดการเชื่อมต่อ WebSocket"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """ส่งข้อความไปยัง WebSocket เฉพาะ"""
        await websocket.send_text(message)

    async def broadcast(self, data: dict):
        """ส่งข้อความไปยัง WebSocket ทั้งหมด"""
        message = json.dumps(data, ensure_ascii=False)
        print(f"Broadcasting to {len(self.active_connections)} WebSocket connections")
        print(f"Message content: {data}")
        
        if not self.active_connections:
            print("No active WebSocket connections to broadcast to")
            return
        
        disconnected_connections = []
        successful_sends = 0
        
        for connection in self.active_connections:
            try:
                # ตรวจสอบสถานะการเชื่อมต่อก่อนส่ง
                if connection.client_state.value == 1:  # CONNECTED
                    await connection.send_text(message)
                    successful_sends += 1
                    print(f"Message sent successfully to WebSocket connection")
                else:
                    print(f"WebSocket connection is not active (state: {connection.client_state.value})")
                    disconnected_connections.append(connection)
            except Exception as e:
                print(f"Error sending message to WebSocket: {e}")
                disconnected_connections.append(connection)
        
        # ลบ connection ที่มีปัญหา
        for connection in disconnected_connections:
            if connection in self.active_connections:
                self.active_connections.remove(connection)
                print(f"Removed failed WebSocket connection")
        
        print(f"Broadcast result: {successful_sends}/{len(self.active_connections + disconnected_connections)} successful")

# สร้าง instance สำหรับใช้งาน
manager = ConnectionManager()
