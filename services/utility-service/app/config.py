from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    SERVICE_NAME: str
    SERVICE_API_KEY: str
    AUTH_SERVICE_URL: str
    NOTIFICATION_SERVICE_URL: str
    ROOT_PATH: str | None = None
    SERVICE_REGISTRATION_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")


settings = Settings()