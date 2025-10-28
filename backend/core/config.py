import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "LangGraph Agent API"
    
    # CORS settings
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8080", "http://localhost:5173"]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///test.db")
    
    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret_key_for_development_only")
    
    # LLM API Keys (should be set in environment variables)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    class Config:
        case_sensitive = True

settings = Settings()