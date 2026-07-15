from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта пользователя")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Пароль, минимум 6 символов")


class UserResponse(UserBase):
    id: int
    telegram_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
