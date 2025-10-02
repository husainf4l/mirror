from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "Wedding Mirror"
    VERSION: str = "1.0.0"
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql:///mirror?user=husain"
    DATABASE_SCHEMA: str = "mirror_app"
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # LiveKit settings (will be loaded from environment)
    LIVEKIT_URL: str = ""  # Set via LIVEKIT_URL env var
    LIVEKIT_API_KEY: str = ""  # Set via LIVEKIT_API_KEY env var  
    LIVEKIT_API_SECRET: str = ""  # Set via LIVEKIT_API_SECRET env var
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()
