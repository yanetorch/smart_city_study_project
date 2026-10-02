from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import AsyncSessionLocal, engine
from app.models import ServiceApiKey
from app.routers import auth, users
from app.security import hash_api_key

async def seed_service_key(session: AsyncSession):
    result = await session.execute(select(ServiceApiKey).where(ServiceApiKey.service_name == settings.SERVICE_NAME))
    existing = result.scalar_one_or_none()

    if existing is None:
        key_hash = hash_api_key(settings.SERVICE_API_KEY)
        service_api_key = ServiceApiKey(service_name=settings.SERVICE_NAME, key_hash = key_hash)
        print('Created api_key for ' + settings.SERVICE_NAME)
        session.add(service_api_key)
        await session.commit()
    else:
        print('Api_key for service ' + settings.SERVICE_NAME + " already exists") 

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await seed_service_key(session)

    yield

    await engine.dispose()


app = FastAPI(title="Identity & Auth Service", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
