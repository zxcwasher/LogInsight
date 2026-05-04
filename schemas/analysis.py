
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnalysisRead(BaseModel):
    id: int
    key: str
    pattern: str
    severity: str
    message: str
    category: str
    service: Optional[str] = None
    description: Optional[str] = None
    source: str
    enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime

class AnalysisResult(BaseModel):
    matched: bool
    pattern_id: Optional[int]
    pattern_key: Optional[str]
    severity: Optional[str]
    category: Optional[str]
    service: Optional[str]
    message: Optional[str]
    normalized_message: Optional[str]
    raw_log: str