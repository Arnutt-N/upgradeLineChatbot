# api/index.py - Vercel serverless function entry point
import os
import sys
from pathlib import Path

# Add parent directory to Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Set environment for Vercel
os.environ["VERCEL"] = "1"

# Import FastAPI app
from app.main import app

# Export app for Vercel
handler = app
