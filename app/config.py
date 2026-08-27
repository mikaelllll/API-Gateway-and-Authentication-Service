from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    app_env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./gateway.db"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str = Field(default="development-secret-change-before-production", min_length=32)
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    cors_origins: list[str] | str = ["http://localhost:5173", "http://localhost:8000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value):
        return [item.strip() for item in value.split(",")] if isinstance(value, str) else value

@lru_cache
def get_settings() -> Settings:
    return Settings()

