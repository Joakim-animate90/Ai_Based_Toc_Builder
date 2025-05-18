import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI-Based TOC Builder"
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    
    # PDF Processing
    PDF_MAX_PAGES: int = 20
    PDF_OUTPUT_DIR: str = "toc"
    
    # Performance
    DEFAULT_THREAD_COUNT: int = max(1, os.cpu_count() - 1) if os.cpu_count() else 2
    
    class Config:
        case_sensitive = True

# Create global settings object
settings = Settings()
