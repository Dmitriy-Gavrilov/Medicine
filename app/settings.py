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

    @property
    def JWT_ACCESS_TOKEN_EXPIRES(self):
        return self.JWT_ACCESS_TOKEN_EXPIRES

    @property
    def JWT_REFRESH_TOKEN_EXPIRES(self):
        return self.JWT_REFRESH_TOKEN_EXPIRES

    model_config = SettingsConfigDict(env_file=".env")

    def get_db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
