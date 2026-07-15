import bcrypt
import jwt
from jwt.exceptions import PyJWTError

from datetime import datetime, timedelta, timezone
from src.config import settings
from typing import Optional


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Принимает чистый пароль, генерирует случайную соль
        и возвращает безопасный хэш в виде строки.
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)

        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Сравнивает чистый пароль, введенный пользователем,
        с хэшем, сохраненным в базе данных.
        """
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        return bcrypt.checkpw(password_bytes, hashed_bytes)

    @staticmethod
    def create_access_token(user_id: int) -> str:
        """Генерирует JWT токен, в который вшит ID пользователя."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user_id),
            "exp": expire
        }

        encoded_jwt = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str) -> Optional[int]:
        """
        Расшифровывает JWT-токен.
        Возвращает id пользователя (int), если токен валиден, иначе None.
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
            return int(user_id)
        except (PyJWTError, ValueError):
            return None
