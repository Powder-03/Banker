from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    project_name: str = "Indian Bank API"
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite+aiosqlite:///./indian_banks.db"
    
    class Config:
        env_file = ".env"

settings = Settings()
