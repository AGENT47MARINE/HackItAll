"""Application configuration."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./opportunity_platform.db")
    
    # Security (kept for backward compatibility with password hashing)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Notification Services
    SMTP_HOST = os.getenv("SMTP_HOST", "")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMS_API_KEY = os.getenv("SMS_API_KEY", "")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Application
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM & AI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    DEFAULT_SCRAPER_MODEL = os.getenv("DEFAULT_SCRAPER_MODEL", "gemma3:4b")


config = Config()
