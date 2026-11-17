from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, Base, AsyncSessionLocal
from .routers import environment
from .seed import seed
from .service_registration import register_self

@asynccontextmanager
async def lifespan(app: FastAPI):
    await register_self()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed(session)

    yield

    await engine.dispose()


app = FastAPI(title="Environment Service", lifespan=lifespan)

app.include_router(environment.router)