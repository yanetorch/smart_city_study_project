import logging

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import settings

log = logging.getLogger(settings.SERVICE_NAME)

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: int
    username: str


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if creds is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(
                f"{settings.AUTH_SERVICE_URL}/users/me",
                headers={"Authorization": f"Bearer {creds.credentials}"},
            )
    except httpx.HTTPError as e:
        log.error("Auth service unavailable: %s", e)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Auth service unavailable")

    if resp.status_code == 401:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if resp.status_code != 200:
        log.error("Unexpected answer from auth service: %s %s", resp.status_code, resp.text)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "Bad response from auth service")

    data = resp.json()
    return CurrentUser(id=data["id"], username=data["username"])
