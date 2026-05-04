from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.log_analysis import (
    ExtractedLogFields,
    EventContext,
    IncidentContext,
    RuleMetadataSnapshot,
)


class ProcessLogRequest(BaseModel):
    raw_log: str
    source: str = "log"
    host: Optional[str] = None
    timestamp: Optional[datetime] = None


class ProcessLogResponse(BaseModel):
    incident_id: int
    event_id: int

    pattern_key: str
    severity: str
    category: str
    service: Optional[str] = None
    message: str

    extracted_fields: ExtractedLogFields
    rule_metadata: RuleMetadataSnapshot
    event_context: EventContext
    incident_context: IncidentContext
    confidence: float
    explanation: list[str]