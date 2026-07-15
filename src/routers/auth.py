import bcrypt


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
