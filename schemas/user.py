from pydantic import BaseModel, field_validator, EmailStr
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
    VIEWER = "viewer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: UserRole

class Config:
    model_config = {"from_attributes": True}


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Пароль должен быть не меньше 8 символов")
        if not any(c.islower() for c in v):
            raise ValueError("Добавь хотя бы одну маленькую букву")
        if not any(c.isupper() for c in v):
            raise ValueError("Добавь хотя бы одну заглавную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Добавь хотя бы одну цифру")
        if not any(not c.isalnum() for c in v):
            raise ValueError("Добавь хотя бы один спецсимвол")
        return v


class UserLogin(BaseModel):
    username: str
    password: str