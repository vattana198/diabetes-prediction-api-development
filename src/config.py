"""
Configuration settings for the Diabetes Prediction API
"""
import os
from typing import List


class Settings:
    """Application settings loaded from environment variables"""
    
    # Server configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # API configuration
    API_TITLE: str = "Diabetes Prediction API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API for predicting diabetes risk based on patient features"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", 
        "*"
    ).split(",") if os.getenv("CORS_ORIGINS") != "*" else ["*"]
    
    # Model paths
    BASE_DIR: str = os.getenv("BASE_DIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def reload_enabled(self) -> bool:
        """Check if auto-reload should be enabled (disabled in production)"""
        return not self.is_production


# Global settings instance
settings = Settings()

