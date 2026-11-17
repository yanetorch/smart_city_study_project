import asyncio
from hashlib import sha256
import logging

import httpx

from app.config import settings

logger = logging.getLogger(settings.SERVICE_NAME)


def hash_api_key(raw: str) -> str:
    return sha256(raw.encode("utf-8")).hexdigest()


async def register_self() -> None:
    if not settings.SERVICE_REGISTRATION_TOKEN:
        logger.warning("Registration token not set")
        return

    url = f"{settings.AUTH_SERVICE_URL}/internal/services/register"
    payload = {"service_name": settings.SERVICE_NAME, "key_hash": hash_api_key(settings.SERVICE_API_KEY)}
    headers = {"X-Registration-Token": settings.SERVICE_REGISTRATION_TOKEN}

    async with httpx.AsyncClient(timeout=10) as client:
        for attempt in range(5):
            try:
                response = await client.post(url, json=payload, headers=headers)
                if response.status_code in (200, 201):
                    logger.info("Registered service: %s", settings.SERVICE_NAME)
                    return
                logger.warning("Registration failed: %s %s", response.status_code, response.text)
            except httpx.HTTPError as e:
                logger.warning("Registration attempt %s failed: %s", attempt + 1, e)
            await asyncio.sleep(2 ** attempt)

    logger.error("Could not register service ", settings.SERVICE_NAME)