from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from models.user import User


async def get_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def get_by_email_or_username(db: AsyncSession, email: str, username: str):
    result = await db.execute(
        select(User).where(
            or_(User.email == email, User.username == username)
        )
    )
    return result.scalar_one_or_none()

async def create(db: AsyncSession, user: User):
    print("DEBUG: Type of user in create():", type(user))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def save(db: AsyncSession, user: User):
    await db.commit()
    await db.refresh(user)
    return user


async def delete(db: AsyncSession, user: User):
    await db.delete(user)
    await db.commit()