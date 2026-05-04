from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from models.analysis import Analysis


async def get_active_patterns(db: AsyncSession):
    result = await db.execute(
        select(Analysis)
        .where(Analysis.enabled.is_(True))
        .order_by(desc(Analysis.priority))
    )
    return result.scalars().all()


async def get_pattern_by_key(db: AsyncSession, key: str):
    result = await db.execute(
        select(Analysis).where(Analysis.key == key)
    )
    return result.scalar_one_or_none()


async def create_pattern(db: AsyncSession, pattern: Analysis):
    db.add(pattern)
    await db.commit()
    await db.refresh(pattern)
    return pattern