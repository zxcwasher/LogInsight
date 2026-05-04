from typing import Optional
from pydantic import BaseModel, Field


class ExtractedLogFields(BaseModel):
    log_level: Optional[str] = None
    status_code: Optional[int] = None
    exception_type: Optional[str] = None


class RuleMetadataSnapshot(BaseModel):
    rule_id: Optional[int] = None
    rule_key: Optional[str] = None
    rule_version: Optional[int] = None
    rule_priority: Optional[int] = None
    rule_source: Optional[str] = None
    rule_enabled: Optional[bool] = None


class EventContext(BaseModel):
    raw_log: str

    matched_rule_key: Optional[str] = None
    matched_rule_version: Optional[int] = None

    log_level: Optional[str] = None
    status_code: Optional[int] = None
    exception_type: Optional[str] = None

    confidence: Optional[float] = None
    explanation: list[str] = Field(default_factory=list)


class IncidentContext(BaseModel):
    primary_service: Optional[str] = None
    primary_error_type: Optional[str] = None
    highest_log_level: Optional[str] = None
    last_status_code: Optional[int] = None

    event_count: int = 0
    confidence_avg: Optional[float] = None