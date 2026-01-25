from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pydantic import field_validator


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"  # Ignore extra environment variables
    )
    
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
    
    # Admin Auto-Creation (Docker)
    create_admin: str = "false"
    admin_email: str = ""
    admin_password: str = ""
    admin_name: str = ""
    
    # MinIO Object Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket_name: str = "academy-assignments"
    minio_secure: str = "false"
    
    @field_validator('backend_url', 'frontend_url')
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        """Remove trailing slash from URLs"""
        return v.rstrip('/')
    
    @property
    def minio_use_ssl(self) -> bool:
        """Convert minio_secure string to boolean"""
        return self.minio_secure.lower() == "true"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
