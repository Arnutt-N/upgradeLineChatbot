# app/core/config.py
import os
from dotenv import load_dotenv

# โหลดค่าจาก .env
load_dotenv()

class Settings:
    # LINE Bot Configuration
    LINE_CHANNEL_SECRET: str = os.getenv('LINE_CHANNEL_SECRET', '')
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./chatbot.db')
    
    # Application Configuration
    APP_TITLE: str = "LINE Bot with Full Live Chat System"
    APP_VERSION: str = "1.3.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # Templates Directory
    TEMPLATES_DIR: str = "templates"

settings = Settings()
