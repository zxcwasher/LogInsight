from enum import Enum
from pydantic import BaseModel

class IncidentCreate(BaseModel):
    title: str
    description: str | None = None
    severity: str


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class UpdateStatus(BaseModel):
    status: IncidentStatus


class UpdateSeverity(BaseModel):
    severity: str