from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.database import get_async_session
from src.storage.models import Users
from src.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> Users:
    """
    Зависимость для защиты эндпоинтов.
    Проверяет JWT токен и возвращает текущего пользователя из БД.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = AuthService.verify_access_token(token)
    if user_id is None:
        raise credentials_exception

    user = await db.get(Users, user_id)
    if user is None:
        raise credentials_exception

    return user
