from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки сервиса уведомлений.

    Все значения можно переопределить через переменные окружения
    или через файл .env (см. config.env.example).
    """

    SERVICE_NAME: str = "notification-service"

    # ---- SMTP (Email) ----
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_password"
    EMAILS_FROM_EMAIL: str = "noreply@smartcity.com"
    EMAILS_FROM_NAME: str = "Smart City"

    # ---- Безопасность (service-to-service) ----
    # Если INTERNAL_API_KEY не задан (None) — проверка ключа ОТКЛЮЧЕНА.
    # Если задан — внутренние запросы обязаны присылать X-Internal-Api-Key.
    INTERNAL_API_KEY: str | None = None
    SERVICE_API_KEY: str | None = None

    # ---- Внешние сервисы ----
    # Чтобы по user_id получить email/телефон — идём в auth-service
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    AUTH_TIMEOUT_SECONDS: float = 3.0

    # ---- Поведение ----
    # Если True — не отправляем реально, только пишем в лог (удобно для тестов)
    DRY_RUN: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()