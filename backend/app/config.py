import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TruthLens AI"
    VERSION: str = "2.1.0"
    API_PREFIX: str = "/api"
    
    # Server configuration
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    # Security & Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "truthlens_super_secret_production_key_2026_jwt_auth_hash")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]
    
    # Database Configuration (Defaults to SQLite for instant local zero-config run, auto-switches to PostgreSQL/Supabase if provided)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./truthlens.db"
    )
    
    # Supabase credentials (optional for cloud storage / DB)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "truthlens-uploads")
    
    # Model configuration
    MODELS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "model")
    BERT_CHECKPOINT: str = os.path.join(MODELS_DIR, "bert_ai_detector", "checkpoint-1500")
    ML_MODELS_DIR: str = os.path.join(MODELS_DIR, "ml_models")
    
    # Device
    USE_CUDA: bool = True
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
