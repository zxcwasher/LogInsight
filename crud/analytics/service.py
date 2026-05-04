from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.incident import Incident


async def get_analytics_summary(db: AsyncSession, user_id: int):
    total_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(Incident.user_id == user_id)
    )

    open_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(
            Incident.user_id == user_id,
            Incident.status == "open",
        )
    )

    investigating_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(
            Incident.user_id == user_id,
            Incident.status == "investigating",
        )
    )

    resolved_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(
            Incident.user_id == user_id,
            Incident.status == "resolved",
        )
    )

    ignored_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(
            Incident.user_id == user_id,
            Incident.status == "ignored",
        )
    )

    critical_incidents = await db.scalar(
        select(func.count(Incident.id))
        .where(
            Incident.user_id == user_id,
            Incident.severity == "critical",
        )
    )

    return {
        "total_incidents": total_incidents or 0,
        "open_incidents": open_incidents or 0,
        "investigating_incidents": investigating_incidents or 0,
        "resolved_incidents": resolved_incidents or 0,
        "ignored_incidents": ignored_incidents or 0,
        "critical_incidents": critical_incidents or 0,
    }