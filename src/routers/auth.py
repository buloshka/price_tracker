from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.storage.database import get_async_session
from src.storage.models import Users
from src.storage.schemas import UserData, UserResponse, TokenResponse
from src.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя"
)
async def sign_up(
        user_data: UserData,
        db: AsyncSession = Depends(get_async_session)
):
    """
    Эндпоинт для регистрации пользователя:
    - Проверяет уникальность email
    - Хэширует пароль
    - Сохраняет данные в базу данных PostgreSQL в Docker
    """
    query = select(Users).where(Users.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован"
        )

    hashed_password = AuthService.hash_password(user_data.password)

    new_user = Users(
        email=user_data.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему (получение JWT-токена)"
)
async def login(
        user_data: UserData,
        db: AsyncSession = Depends(get_async_session)
):
    """Эндпоинт авторизации:
    - проверяет учетные данные
    - возвращает JWT-токен"""
    # 1. Ищем пользователя по email
    query = select(Users).where(Users.email == user_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user or not AuthService.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или password"
        )

    token = AuthService.create_access_token(user_id=user.id)

    return {"access_token": token, "token_type": "bearer"}
