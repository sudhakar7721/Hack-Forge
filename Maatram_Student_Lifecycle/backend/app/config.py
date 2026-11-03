from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    APP_NAME: str = "MH26-05 Maatram Student Lifecycle"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "sqlite:///./maatram_dev.db"
    JWT_SECRET: str = "development-only-change-this-secret-please"
    JWT_EXPIRE_MINUTES: int = 60
    CORS_ORIGINS: str = "http://localhost:5173"
    UPLOAD_DIR: str = "./storage/private"
    MAX_UPLOAD_MB: int = 8
    OTP_MODE: str = "console"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
