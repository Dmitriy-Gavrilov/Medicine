from passlib.context import CryptContext


class PasswordHasher:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    async def hash_password(password: str) -> str:
        return PasswordHasher.pwd_context.hash(password)

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        return PasswordHasher.pwd_context.verify(plain_password, hashed_password)
