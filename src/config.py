from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    DB_NAME: str
    PORT: int = 8000
    CORS_ORIGINS: str = "*"
    REQUEST_TIMEOUT: int = 10
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        env_file = ".env"

settings = Settings()