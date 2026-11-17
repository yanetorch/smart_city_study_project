from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str | None = None
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    SERVICE_NAME: str
    SERVICE_API_KEY: str
    
    SERVICE_REGISTRATION_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")

settings = Settings()