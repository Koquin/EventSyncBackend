from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "eventsync"
    
    # JWT Configuration
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Configuration
    APP_NAME: str = "EventSync API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    PORT: int = 3001
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
