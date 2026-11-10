from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:123@localhost:5432/utility"
    SERVICE_NAME: str = "utility"

    AUTH_SERVICE_URL: str = "http://localhost:8001"
    NOTIFICATION_SERVICE_URL: str = ""

    ROOT_PATH: str = ""

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")


settings = Settings()
