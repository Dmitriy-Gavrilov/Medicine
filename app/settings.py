from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_NAME: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str

    echo: bool = False

    JWT_SECRET_KEY: str
    JWT_COOKIE_NAME: str
    JWT_REFRESH_COOKIE_NAME: str
    JWT_ACCESS_TOKEN_EXPIRES: int
    JWT_REFRESH_TOKEN_EXPIRES: int

    REDIS_HOST: str
    REDIS_PORT: int

    ROUTE_API_URL: str = "https://router.project-osrm.org/route/v1/driving"

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
