from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TempShell"
    ENVIRONMENT: str = "production"
    API_V1_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int = 3306
    
    # Kubernetes
    K8S_NAMESPACE: str = "tempshell"
    POD_IMAGE: str = "ubuntu:22.04"
    POD_CPU_REQUEST: str = "100m"
    POD_CPU_LIMIT: str = "500m"
    POD_MEMORY_REQUEST: str = "128Mi"
    POD_MEMORY_LIMIT: str = "256Mi"
    POD_TIMEOUT_SECONDS: int = 3600
    
    # CORS - Parse from string to list
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Parse CORS_ORIGINS if it's a string
        if isinstance(self.CORS_ORIGINS, str):
            import json
            try:
                self.CORS_ORIGINS = json.loads(self.CORS_ORIGINS)
            except:
                self.CORS_ORIGINS = [origin.strip() for origin in self.CORS_ORIGINS.split(',')]

settings = Settings()
