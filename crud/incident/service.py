from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from crud.incident.repository import (
    get_incident_by_id,
    create_incident,
    find_open_incident_by_fingerprint,
)
from models.incident import Incident, Status, Severity, IncidentHistory


ALLOWED_TRANSITIONS = {
    Status.OPEN: [Status.INVESTIGATING],
    Status.INVESTIGATING: [Status.RESOLVED],
    Status.RESOLVED: [],
}


async def create_incident_service(
    title: str,
    analysis: str,
    severity: str,
    user_id: int,
    pattern_key: str,
    service: str,
    category: str,
):
    try:
        enum_severity = Severity(severity)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid severity")

    incident = Incident(
        title=title,
        analysis=analysis,
        user_id=user_id,
        status=Status.OPEN.value,
        severity=enum_severity.value,
        pattern_key=pattern_key,
        service=service,
        category=category,
    )

    return incident

async def create_or_find_incident(db, user_id: int, analysis_result):
    existing_incident = await find_open_incident_by_fingerprint(
        db=db,
        user_id=user_id,
        service=analysis_result.service,
        category=analysis_result.category,
        pattern_key=analysis_result.pattern_key,
    )

    if existing_incident:
        return existing_incident

    incident = Incident(
        user_id=user_id,
        title=analysis_result.message,
        service=analysis_result.service,
        category=analysis_result.category,
        severity=analysis_result.severity,
        status="open",
        pattern_key=analysis_result.pattern_key,
    )

    db.add(incident)
    await db.commit()
    await db.refresh(incident)

    return incident


async def update_incident_field(
    db: AsyncSession,
    field: str,
    incident_id: int,
    new_value: str,
    current_user,
):
    incident = await get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_value = getattr(incident, field)

    if field == "status":
        try:
            old_status = Status(old_value)
            new_status = Status(new_value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

        allowed = ALLOWED_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transition from {old_status.value} to {new_status.value}",
            )

        setattr(incident, field, new_status.value)

        history = IncidentHistory(
            incident_id=incident.id,
            user_id=current_user.id,
            old_status=old_status.value,
            new_status=new_status.value,
            changed_at=datetime.utcnow(),
        )
        db.add(history)
    else:
        setattr(incident, field, new_value)

    await db.commit()
    await db.refresh(incident)
    return incident



async def update_incident(
    db: AsyncSession,
    incident_id: int,
    title: str | None = None,
):
    incident = await get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if title is not None:
        incident.title = title

    await db.commit()
    await db.refresh(incident)

    return incident