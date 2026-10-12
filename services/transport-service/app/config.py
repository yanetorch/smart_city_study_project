from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # значения по умолчанию — для локального запуска без докера,
    # в docker-compose всё переопределяется через environment
    DATABASE_URL: str = "postgresql+asyncpg://admin:123@localhost:5432/transport"
    SERVICE_NAME: str = "transport"

    # куда ходить проверять токен (GET /users/me)
    AUTH_SERVICE_URL: str = "http://localhost:8001"
    # пусто = уведомления не отправляются (пока Notification Service не готов)
    NOTIFICATION_SERVICE_URL: str = ""

    # префикс, под которым сервис висит за nginx (нужен для Swagger)
    ROOT_PATH: str = ""

    model_config = SettingsConfigDict(env_file="config.env", extra="ignore")


settings = Settings()
