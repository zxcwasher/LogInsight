from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from crud.user.service import register as register_user_service
from crud.user.service import login
from models.helper import get_db
from schemas.user import UserRegister, UserLogin
from utils.jwt import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(
    user: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    new_user = await register_user_service(db, user)
    token = create_token({"sub": str(new_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": new_user.id,
    }


@router.post("/login")
async def login_user(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    return await login(db, user_data)


@router.get("/me")
async def get_me(
    current_user=Depends(get_current_user),
):
    return current_user