import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, status

from app.config import settings
from app.notifications import process_notification
from app.schemas import NotificationRequest, NotificationResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(settings.SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.INTERNAL_API_KEY:
        logger.info("Starting %s (auth: ENABLED, dry_run=%s)",
                    settings.SERVICE_NAME, settings.DRY_RUN)
    else:
        logger.warning(
            "Starting %s (auth: DISABLED — INTERNAL_API_KEY not set, dry_run=%s)",
            settings.SERVICE_NAME, settings.DRY_RUN,
        )
    yield
    logger.info("Stopping %s", settings.SERVICE_NAME)


app = FastAPI(title=settings.SERVICE_NAME, lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "auth_enabled": bool(settings.INTERNAL_API_KEY),
    }


@app.post(
    "/notifications",
    response_model=NotificationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Внутренний эндпоинт отправки уведомления",
)
async def send_notification(
    payload: NotificationRequest,
    background_tasks: BackgroundTasks,
    # Опциональный заголовок — если INTERNAL_API_KEY не задан, можно не присылать
    x_internal_api_key: str | None = Header(None, alias="X-Internal-Api-Key"),
):
    """Принимает запрос от других сервисов и ставит отправку в фон.

    Если в настройках задан INTERNAL_API_KEY — требуется заголовок
    X-Internal-Api-Key с этим ключом. Если ключ не задан — проверка
    пропускается (режим разработки / изолированная docker-сеть).
    """
    # 1. Авторизация service-to-service (только если ключ настроен)
    if settings.INTERNAL_API_KEY:
        if x_internal_api_key != settings.INTERNAL_API_KEY:
            logger.warning(
                "Rejected: invalid internal API key (source=%s)", payload.source,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid internal API key",
            )

    # 2. Ставим в фон
    task_id = str(uuid.uuid4())
    background_tasks.add_task(
        process_notification,
        user_id=payload.user_id,
        title=payload.title,
        message=payload.message,
        source=payload.source,
        channel=payload.channel.value,
        recipient_override=payload.recipient_override,
    )

    logger.info(
        "Notification queued: task=%s user=%s channel=%s source=%s",
        task_id, payload.user_id, payload.channel.value, payload.source,
    )
    return NotificationResponse(status="queued", task_id=task_id)