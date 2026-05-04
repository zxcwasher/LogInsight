from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user import UserRegister, UserLogin
from models.user import User
from utils.security import get_password_hash, verify_hash
from utils.jwt import create_token

import crud.user.repository as repo


async def register(db: AsyncSession, user_data: UserRegister):
    existing = await repo.get_by_email_or_username(
        db, user_data.email, user_data.username
    )

    if existing:
        raise HTTPException(409, "Username or Email already exists")

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
    )
    new_user = await repo.create(db, db_user)
    return new_user


async def login(db: AsyncSession, user_data: UserLogin):
    user = await repo.get_by_username(db, user_data.username)

    if not user or not verify_hash(user_data.password, user.hashed_password):
        raise HTTPException(401, "Неверные учетные данные")

    token = create_token({"sub": str(user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


async def update_user(
    db: AsyncSession,
    user_id: int,
    username: str | None = None,
    email: str | None = None,
    password: str | None = None
):
    user = await repo.get_by_id(db, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    if username:
        user.username = username

    if email:
        user.email = email

    if password:
        user.hashed_password = get_password_hash(password)

    return await repo.save(db, user)


async def delete_user(db: AsyncSession, user_id: int):
    user = await repo.get_by_id(db, user_id)

    if not user:
        raise HTTPException(404, "User not found")

    await repo.delete(db, user)
    return True