
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class EventRead(BaseModel):
    id: int
    incident_id: int
    pattern_id: int | None = None
    user_id: int
    pattern_key: str
    timestamp: datetime
    service: Optional[str] = None
    raw_message: str
    severity: str
    message: str
    host: Optional[str] = None
    created_at: datetime
    source: str
    category: str