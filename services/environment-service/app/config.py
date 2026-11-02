from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str  # Должен совпадать с тем, что в auth_service!
    ALGORITHM: str = "HS256"
    SERVICE_NAME: str

    # Для Billing сервиса добавим ключ для внутренних запросов (webhook)
    SERVICE_API_KEY: str = ""

    class Config:
        env_file = "config.env"


settings = Settings()