from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    PROJECT_NAME: str = "Web Capture Pro"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Supabase 설정
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Database URL for SQLAlchemy (will be provided by Supabase)
    DATABASE_URL: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
