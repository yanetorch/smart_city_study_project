import logging

import httpx

from app.config import settings

log = logging.getLogger(settings.SERVICE_NAME)


async def send_notification(user_id: int, title: str, message: str) -> None:
    """Отправка уведомления в Notification Service.

    Уведомление — не критичная операция: если сервис уведомлений
    недоступен, основная операция всё равно считается успешной.
    """
    if not settings.NOTIFICATION_SERVICE_URL:
        log.info("Notification skipped (NOTIFICATION_SERVICE_URL not set): user=%s '%s'", user_id, title)
        return

    payload = {"user_id": user_id, "title": title, "message": message, "source": settings.SERVICE_NAME}
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.post(f"{settings.NOTIFICATION_SERVICE_URL}/notifications", json=payload)
            resp.raise_for_status()
        log.info("Notification sent to user %s: '%s'", user_id, title)
    except httpx.HTTPError as e:
        log.warning("Failed to send notification to user %s: %s", user_id, e)
