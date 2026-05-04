from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.permissions import require_roles
from crud.incident.repository import (
    get_incidents,
    get_incident_by_id,
    delete_incident,
)
from crud.incident.service import update_incident, update_incident_field
from crud.log_processing.service import process_log
from models.helper import get_db
from schemas.incident import IncidentCreate, UpdateStatus, UpdateSeverity
from sqlalchemy import select
from models.event import Event
from crud.event.repository import get_events_by_incident_id

router = APIRouter(prefix="/incident", tags=["incident"])


@router.post("")
async def add_incident_route(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    result = await process_log(
        db=db,
        user_id=current_user.id,
        raw_log=incident.logs,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No matching pattern found",
        )

    return result


@router.get("/")
async def get_all_incidents_route(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    return await get_incidents(db)


@router.get("/{incident_id}")
async def get_incident_id_route(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    incident = await get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident


@router.put("/{incident_id}")
async def update_incident_route(
    incident_id: int,
    title_text: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    return await update_incident(
        db=db,
        incident_id=incident_id,
        title=title_text,
    )


@router.delete("/{incident_id}")
async def delete_incident_route(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    incident = await get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    await delete_incident(db, incident)

    return {"status": "deleted"}


@router.put("/{incident_id}/status")
async def update_incident_status(
    incident_id: int,
    update_data: UpdateStatus,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    return await update_incident_field(
        db=db,
        incident_id=incident_id,
        field="status",
        new_value=update_data.status,
        current_user=current_user,
    )


@router.put("/{incident_id}/severity")
async def update_incident_severity(
    incident_id: int,
    update_data: UpdateSeverity,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer")),
):
    return await update_incident_field(
        db=db,
        incident_id=incident_id,
        field="severity",
        new_value=update_data.severity,
        current_user=current_user,
    )

@router.get("/{incident_id}/events")
async def get_incident_timeline(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(require_roles("admin", "engineer", "viewer")),
):
    incident = await get_incident_by_id(db, incident_id)

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    events = await get_events_by_incident_id(db, incident_id)

    return {
        "incident_id": incident_id,
        "event_count": len(events),
        "events": events,
    }