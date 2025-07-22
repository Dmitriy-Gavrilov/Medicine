from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_NAME: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    echo: bool = False

    JWT_SECRET_KEY: str
    JWT_COOKIE_NAME: str
    JWT_REFRESH_COOKIE_NAME: str
    JWT_ACCESS_TOKEN_EXPIRES: timedelta
    JWT_REFRESH_TOKEN_EXPIRES: timedelta

    @property
    def JWT_COOKIE_MAX_AGE(self) -> float:
        return self.JWT_ACCESS_TOKEN_EXPIRES.total_seconds()

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    ROUTE_API_URL: str = "https://router.project-osrm.org/route/v1/driving"

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_NAME}"


settings = Settings()
