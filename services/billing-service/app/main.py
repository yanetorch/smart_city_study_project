from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, Base, AsyncSessionLocal
from .routers import billing
from . import models  # <-- КРИТИЧЕСКИ ВАЖНО
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed(session)

    yield

    await engine.dispose()


app = FastAPI(title="Billing Service", lifespan=lifespan)

app.include_router(billing.router)