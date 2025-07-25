# LINE Bot Chatbot with Admin Panel

A comprehensive LINE Bot application with dual admin systems, real-time chat capabilities, and advanced analytics.

## Project Structure

```
upgradeLineChatbot/
├── backend/          # FastAPI Backend Application
├── frontend/         # Templates & Static Assets  
├── scripts/          # Utility Scripts
├── config/           # Configuration Files
├── docs/             # Documentation
├── tests/            # Test Files
└── tools/            # Development Tools
```

## Quick Start

### Backend Development
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Production Deployment
```bash
# Using Docker
docker-compose -f config/docker-compose.yml up --build

# Using Python directly
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Features

- **LINE Bot Integration**: Real-time webhook processing
- **Dual Admin Systems**: Live chat + Form management
- **Analytics Dashboard**: Real-time data visualization
- **Telegram Integration**: Admin notifications
- **AI-Powered Responses**: Gemini AI integration

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL/SQLite
- **Frontend**: HTML5, CSS3, JavaScript, WebSocket
- **AI**: Google Gemini API
- **Deployment**: Docker, Render, Vercel
- **Database**: PostgreSQL (production), SQLite (development)
