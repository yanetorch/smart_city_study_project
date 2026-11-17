from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    SECRET_KEY: str
    SERVICE_NAME: str
    SERVICE_API_KEY: str
    AUTH_SERVICE_URL: str

    SERVICE_REGISTRATION_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")

settings = Settings()