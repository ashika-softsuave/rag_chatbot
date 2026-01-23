from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # App
    APP_NAME: str
    ENVIRONMENT: str
    DEBUG: bool

    # Server
    HOST: str
    PORT: int

    # Security
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    # Database
    DATABASE_URL: str

    # OpenAI
    OPENAI_API_KEY: str

    # SMTP / Email (ADD THIS BLOCK)
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    # Logging
    LOG_LEVEL: str

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings object (singleton)
    """
    return Settings()

