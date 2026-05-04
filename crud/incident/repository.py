from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.incident import Incident, Status

async def find_open_incident_by_fingerprint(
    db: AsyncSession,
    user_id: int,
    service: str,
    category: str,
    pattern_key: str,
):
    query = select(Incident).where(
        Incident.user_id == user_id,
        Incident.service == service,
        Incident.category == category,
        Incident.pattern_key == pattern_key,
        or_(
            Incident.status == "open",
            Incident.status == "investigating",
        ),
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_incidents(db: AsyncSession):
    result = await db.execute(select(Incident))
    return result.scalars().all()


async def get_incident_by_id(db: AsyncSession, incident_id: int):
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    return result.scalar_one_or_none()


async def get_open_incident_by_signature(
    db: AsyncSession,
    user_id: int,
    pattern_key: str,
    service: str | None,
    category: str,
):
    """
       Deduplication rule for incidents:
       one open incident per (user_id, pattern_key, service, category).

       Notes:
       - only incidents with OPEN status participate in deduplication;
       - service=None is treated as a valid part of the signature;
         that means incidents with service=None match only incidents
         where service is also None.
       """

    result = await db.execute(
        select(Incident).where(
            Incident.user_id == user_id,
            Incident.pattern_key == pattern_key,
            Incident.service == service,
            Incident.category == category,
            Incident.status == Status.OPEN.value,
        )
    )
    return result.scalar_one_or_none()


async def create_incident(db: AsyncSession, incident: Incident):
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    return incident


async def delete_incident(db: AsyncSession, incident: Incident):
    await db.delete(incident)
    await db.commit()