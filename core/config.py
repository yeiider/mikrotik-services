from pydantic_settings import BaseSettings
from typing import Optional, List
import json
import os

class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "Mikrotik Metrics Service"
    API_V1_STR: str = "/api/v1"
    
    # Inventory Settings
    ROUTERS_JSON_PATH: str = "routers.json"
    ROUTERS_JSON_ENV: Optional[str] = None # JSON string if config is passed via env
    
    # InfluxDB Settings
    INFLUXDB_URL: str
    INFLUXDB_TOKEN: str
    INFLUXDB_ORG: str
    INFLUXDB_BUCKET: str = "mikrotik_metrics"
    
    # Collector Settings
    COLLECTOR_INTERVAL_SECONDS: int = 300  # 5 minutes

    # Security Settings
    SECURITY_TOKEN: Optional[str] = None
    ALLOWED_IPS: List[str] = []
    ENABLE_TOKEN_CHECK: bool = False
    ENABLE_IP_CHECK: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
