from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    total_incidents: int
    open_incidents: int
    investigating_incidents: int
    resolved_incidents: int
    ignored_incidents: int
    critical_incidents: int