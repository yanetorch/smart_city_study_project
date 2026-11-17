from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import ServiceApiKey
from app.schemas import ServiceRegistrationRequest

router = APIRouter(prefix="/internal/services", tags=["internal-services"])

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_service(payload: ServiceRegistrationRequest, db: AsyncSession = Depends(get_db), x_registration_token: str | None = Header(None, alias="X-Registration-Token")):
    if (x_registration_token != settings.SERVICE_REGISTRATION_TOKEN or not settings.SERVICE_REGISTRATION_TOKEN):
        raise HTTPException(403, "Invalid registration token")

    existing = await db.scalar(select(ServiceApiKey).where(ServiceApiKey.service_name == payload.service_name))
    if existing is None:
        db.add(ServiceApiKey(service_name=payload.service_name, key_hash=payload.key_hash, is_active=True))
        print("Created api_key for " + payload.service_name)
    else:
        existing.key_hash = payload.key_hash
        print("Api_key for " + payload.service_name + "already exists")
    
    await db.commit()