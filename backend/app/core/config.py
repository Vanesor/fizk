import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str = "ZKP Auth API"
    API_PREFIX: str = "/api"
    DEBUG: bool = True

    
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    CHALLENGE_TTL: int = 300  
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  
    }

settings = Settings()