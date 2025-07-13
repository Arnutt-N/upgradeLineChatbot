# app/core/config.py
import os
from dotenv import load_dotenv

# โหลดค่าจาก .env (เฉพาะ development)
load_dotenv()

class Settings:
    # LINE Bot Configuration
    LINE_CHANNEL_SECRET: str = os.getenv('LINE_CHANNEL_SECRET', '')
    LINE_CHANNEL_ACCESS_TOKEN: str = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
    
    # Telegram Configuration (Optional)
    TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHAT_ID: str = os.getenv('TELEGRAM_CHAT_ID', '')
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    GEMINI_TEMPERATURE: float = float(os.getenv('GEMINI_TEMPERATURE', '0.7'))
    GEMINI_MAX_TOKENS: int = int(os.getenv('GEMINI_MAX_TOKENS', '1000'))
    GEMINI_ENABLE_SAFETY: bool = os.getenv('GEMINI_ENABLE_SAFETY', 'true').lower() == 'true'
    
    # Database Configuration
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./chatbot.db')
    
    # Application Configuration
    APP_TITLE: str = "LINE Bot with Full Live Chat System"
    APP_VERSION: str = "1.3.0"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    RELOAD: bool = os.getenv("RELOAD", "true").lower() == "true"
    
    # Templates Directory
    TEMPLATES_DIR: str = "templates"
    
    # Security Settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"
    
    def validate_required_settings(self):
        """Validate that required settings are present"""
        required = []
        
        if not self.LINE_CHANNEL_SECRET:
            required.append("LINE_CHANNEL_SECRET")
        if not self.LINE_CHANNEL_ACCESS_TOKEN:
            required.append("LINE_CHANNEL_ACCESS_TOKEN")
            
        if required:
            raise ValueError(f"Missing required environment variables: {', '.join(required)}")

settings = Settings()

# Note: Settings validation moved to webhook endpoints to prevent startup failures
