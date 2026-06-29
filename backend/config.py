from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "GuardianAI"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "sqlite+aiosqlite:///./guardian.db"
    REDIS_URL: str = "redis://localhost:6379"
    MODEL_DIR: str = "./checkpoints"
    
    # Camera Settings
    CAMERA_WIDTH: int = 640
    CAMERA_HEIGHT: int = 480
    CAMERA_FPS: int = 30
    
    # Risk Thresholds
    RISK_THRESHOLD_LOW: float = 25.0
    RISK_THRESHOLD_MEDIUM: float = 50.0
    RISK_THRESHOLD_HIGH: float = 75.0
    RISK_THRESHOLD_CRITICAL: float = 90.0
    
    # Agent Settings
    INFERENCE_INTERVAL_MS: int = 100
    
    # Cloud Settings
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_BUCKET: str = ""
    USE_CLOUD: bool = False
    
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    class Config:
        env_file = ".env"

settings = Settings()
