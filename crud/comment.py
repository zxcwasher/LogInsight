from sqlalchemy.ext.asyncio import AsyncSession
from models.comment import Comment
from sqlalchemy import select

async def get_comment_by_id (db: AsyncSession, comment_id: int):
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id))
    return result.scalars().one_or_none()

async def get_comment_by_incident(db: AsyncSession, incident_id: int):
    results = await db.execute(
        select(Comment).where(Comment.incident_id == incident_id)
    )
    return results.scalars().all()

async def create_comment(
        db: AsyncSession,
        comment_text: str,
        user_id: int,
        incident_id: int):

    new_comment = Comment(
        comment=comment_text,
        user_id=user_id,
        incident_id=incident_id
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

async def update_comment(
        db: AsyncSession,
        comment_id: int,
        comment_text: str | None = None):

    comment_obj = await get_comment_by_id (db, comment_id)
    if not comment_obj:
        return None

    if comment_text:
        comment_obj.comment = comment_text

    await db.commit()
    await db.refresh(comment_obj)

    return comment_obj

async def delete_comment(db: AsyncSession, comment_id: int):
    comment = await get_comment_by_id(db, comment_id)

    if not comment:
        return None

    await db.delete(comment)
    await db.commit()

    return True