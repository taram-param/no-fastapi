from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NO FastAPI"
    SECRET_KEY: str = "very secret"

    DB_URL: str
    TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/test_db"

    KAFKA_BOOTSTRAP_SERVERS: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
