"""
Configuration settings for the Environmental Safety Platform
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost/environmental_db")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # API Keys (set via environment variables)
    OPENAQ_API_KEY: Optional[str] = os.getenv("OPENAQ_API_KEY")
    GOOGLE_EARTH_ENGINE_CREDENTIALS: Optional[str] = os.getenv("GOOGLE_EARTH_ENGINE_CREDENTIALS")
    MAPBOX_TOKEN: Optional[str] = os.getenv("MAPBOX_TOKEN")
    
    # Data Sources Configuration
    SENTINEL5P_MAX_AGE_DAYS: int = 7  # Consider data stale after 7 days
    GROUND_SENSOR_MAX_AGE_HOURS: int = 24
    WEATHER_DATA_MAX_AGE_HOURS: int = 6
    
    # ML Model Settings
    RISK_MODEL_VERSION: str = "1.0.0"
    FORECAST_HORIZON_HOURS: int = 48
    ANOMALY_DETECTION_WARNING_DAYS: int = 30
    
    # Spatial Settings
    DEFAULT_GRID_RESOLUTION_KM: float = 1.0  # 1km grid for data fusion
    GROUND_SENSOR_SEARCH_RADIUS_KM: float = 50.0
    
    class Config:
        case_sensitive = True

settings = Settings()
