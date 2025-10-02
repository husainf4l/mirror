from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "Wedding Mirror"
    VERSION: str = "1.0.0"
    
    # Environment
    ENVIRONMENT: str = "production"  # development, staging, production
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False  # Changed to False for production
    
    # Cookie settings (production defaults)
    COOKIE_SECURE: bool = True  # HTTPS only
    COOKIE_SAMESITE: str = "none"  # Allow cross-origin
    COOKIE_DOMAIN: str | None = None  # Let browser handle it
    
    # CORS settings
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "https://raheva.com",
        "https://www.raheva.com",
        "http://raheva.com",
        "http://www.raheva.com",
    ]
    
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
