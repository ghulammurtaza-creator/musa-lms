from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/academy_db"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google APIs
    google_client_id: str = ""
    google_client_secret: str = ""
    google_webhook_secret: str = ""
    
    # Google Gemini AI
    gemini_api_key: str = ""
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    @field_validator('backend_url', 'frontend_url')
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        """Remove trailing slash from URLs"""
        return v.rstrip('/')
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
