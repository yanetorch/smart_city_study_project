import logging
from abc import ABC, abstractmethod

import aiosmtplib
import httpx
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

from app.config import settings

logger = logging.getLogger(settings.SERVICE_NAME)


# ---------------------------------------------------------------------------
# Базовый интерфейс отправителя
# ---------------------------------------------------------------------------
class BaseSender(ABC):
    """Абстрактный отправитель. Один класс = один канал доставки."""

    @abstractmethod
    async def send(self, recipient: str, subject: str, message: str) -> None:
        ...


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------
class EmailSender(BaseSender):
    async def send(self, recipient: str, subject: str, message: str) -> None:
        if settings.DRY_RUN:
            logger.info("[DRY_RUN] Email -> %s | %s | %s", recipient, subject, message)
            return

        msg = MIMEMultipart()
        msg["From"] = formataddr((settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL))
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
            timeout=10,
        )
        logger.info("Email sent to %s (subject=%r)", recipient, subject)


# ---------------------------------------------------------------------------
# SMS (заглушка — легко заменить на Twilio / SMSC / провайдера)
# ---------------------------------------------------------------------------
class SMSSender(BaseSender):
    async def send(self, recipient: str, subject: str, message: str) -> None:
        if settings.DRY_RUN:
            logger.info("[DRY_RUN] SMS -> %s | %s", recipient, message)
            return

        # TODO: интеграция с реальным провайдером
        logger.info("[MOCK] SMS -> %s | %s", recipient, message)


# ---------------------------------------------------------------------------
# Push (заглушка — FCM / APNs)
# ---------------------------------------------------------------------------
class PushSender(BaseSender):
    async def send(self, recipient: str, subject: str, message: str) -> None:
        if settings.DRY_RUN:
            logger.info("[DRY_RUN] PUSH -> %s | %s | %s", recipient, subject, message)
            return

        # TODO: интеграция с FCM / APNs
        logger.info("[MOCK] PUSH -> %s | %s", recipient, subject)


# ---------------------------------------------------------------------------
# Фабрика отправителей
# ---------------------------------------------------------------------------
def get_sender(channel: str) -> BaseSender:
    if channel == "email":
        return EmailSender()
    if channel == "sms":
        return SMSSender()
    if channel == "push":
        return PushSender()
    raise ValueError(f"Unsupported channel: {channel}")


# ---------------------------------------------------------------------------
# Резолвер user_id -> контакт (email / телефон)
# ---------------------------------------------------------------------------
async def resolve_contact(user_id: int, channel: str) -> str | None:
    """Получаем email или телефон пользователя из auth-service.

    Если auth-service недоступен или поля нет — возвращаем None,
    уведомление молча пропускается (не критичная операция).
    """
    try:
        async with httpx.AsyncClient(timeout=settings.AUTH_TIMEOUT_SECONDS) as client:
            resp = await client.get(
                f"{settings.AUTH_SERVICE_URL}/users/{user_id}",
                headers={"X-API-Key": settings.SERVICE_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPError as e:
        logger.warning("Cannot resolve contact for user=%s: %s", user_id, e)
        return None

    if channel == "email":
        return data.get("email")
    if channel == "sms":
        return data.get("phone")
    if channel == "push":
        return data.get("push_token")
    return None


# ---------------------------------------------------------------------------
# Главная функция — вызывается из BackgroundTasks
# ---------------------------------------------------------------------------
async def process_notification(
    user_id: int,
    title: str,
    message: str,
    source: str | None,
    channel: str,
    recipient_override: str | None = None,
) -> None:
    """Определить контакт и отправить уведомление по нужному каналу."""
    recipient = recipient_override or await resolve_contact(user_id, channel)

    if not recipient:
        logger.warning(
            "Notification skipped: no %s contact for user=%s (source=%s)",
            channel, user_id, source,
        )
        return

    sender = get_sender(channel)
    try:
        await sender.send(recipient, title, message)
        logger.info(
            "Notification delivered: user=%s source=%s channel=%s",
            user_id, source, channel,
        )
    except Exception as e:
        # Ошибку доставки глушим — это фоновая задача, основной поток не должен падать
        logger.error(
            "Delivery failed: user=%s channel=%s error=%s",
            user_id, channel, e,
        )