# api/main.py - Real FastAPI app for Vercel
from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import urlparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import settings first
try:
    from app.core.config import settings
    CONFIG_LOADED = True
except Exception as e:
    CONFIG_LOADED = False
    CONFIG_ERROR = str(e)

# Simple handler first
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # Route handling
        if path == "/":
            response = {
                "message": "LINE Chatbot API on Vercel",
                "version": "2.9.5",
                "status": "ready",
                "config_loaded": CONFIG_LOADED
            }
        elif path == "/health":
            response = {
                "status": "healthy",
                "service": "LINE Chatbot",
                "environment": os.getenv("ENVIRONMENT", "unknown"),
                "config_loaded": CONFIG_LOADED
            }
        elif path == "/debug":
            response = {
                "status": "debug",
                "python_version": sys.version,
                "env_vars": {
                    "ENVIRONMENT": os.getenv("ENVIRONMENT"),
                    "DB_TYPE": os.getenv("DB_TYPE"),
                    "LINE_CHANNEL_SECRET": "***" if os.getenv("LINE_CHANNEL_SECRET") else None,
                    "DATABASE_URL": "***" if os.getenv("DATABASE_URL") else None
                },
                "config_loaded": CONFIG_LOADED,
                "config_error": CONFIG_ERROR if not CONFIG_LOADED else None
            }
        else:
            response = {"error": "Not found", "path": path}
            
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_POST(self):
        # Handle POST requests
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        
        if path == "/webhook":
            # LINE webhook handling
            response = {
                "status": "webhook received",
                "content_length": content_length,
                "line_signature": self.headers.get('X-Line-Signature', 'not found')
            }
        else:
            response = {
                "status": "received",
                "method": "POST",
                "path": path,
                "content_length": content_length
            }
            
        self.wfile.write(json.dumps(response).encode())
        return
