from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from datetime import datetime

class InfluxPoint(BaseModel):
    measurement: str
    tags: Dict[str, str]
    fields: Dict[str, Any]
    time: Optional[datetime] = None

class InfluxWriteError(BaseModel):
    message: str
    details: Optional[str] = None
