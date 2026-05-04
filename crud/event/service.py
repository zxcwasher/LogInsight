from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from crud.event.repository import create_event
from models.event import Event


async def create_event_service(
    db: AsyncSession,
    user_id: int,
    incident,
    analysis_result: dict,
    source: str = "log",
    host: Optional[str] = None,
    timestamp: Optional[datetime] = None,
):
    new_event = Event(
        incident_id=incident.id,
        user_id=user_id,
        category=analysis_result.get("category", "unknown"),
        pattern_key=analysis_result.get("pattern_key", "unknown"),
        timestamp=timestamp or datetime.utcnow(),
        service=analysis_result.get("service", "unknown"),
        raw_message=analysis_result.get("raw_log", ""),
        severity=analysis_result.get("severity", "low"),
        message=analysis_result.get("message", "Unclassified log"),
        host=host,
        source=source,
    )

    return await create_event(db, new_event)