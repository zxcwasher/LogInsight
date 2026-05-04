from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.event import Event


async def create_event(db: AsyncSession, event: Event):
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event

async def get_events_by_incident_id(
    db: AsyncSession,
    incident_id: int,
):
    query = (
        select(Event)
        .where(Event.incident_id == incident_id)
        .order_by(Event.created_at.asc())
    )

    result = await db.execute(query)
    return result.scalars().all()