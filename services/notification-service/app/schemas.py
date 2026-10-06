from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NotificationChannel(str, Enum):
    """Канал доставки уведомления."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class NotificationRequest(BaseModel):
    """Входящий запрос на отправку уведомления (внутренний API).

    Совместим с вызовом из transport-service / utility-service:
        POST /notifications
        {
            "user_id": 42,
            "title": "Парковка забронирована",
            "message": "...",
            "source": "transport-service"
        }
    """

    user_id: int = Field(..., description="ID пользователя, которому шлём уведомление")
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=4000)
    source: Optional[str] = Field(None, description="Кто отправил (имя сервиса)")
    channel: NotificationChannel = NotificationChannel.EMAIL

    # Если у отправителя уже есть контакт — можно передать его напрямую,
    # тогда notification-service не будет ходить в auth-service.
    recipient_override: Optional[str] = None

    metadata: Optional[dict[str, Any]] = None


class NotificationResponse(BaseModel):
    """Ответ на запрос отправки."""
    status: str
    task_id: str