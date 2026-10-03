from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    SERVICE_NAME: str = "default"
    SERVICE_API_KEY: str

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")

settings = Settings()