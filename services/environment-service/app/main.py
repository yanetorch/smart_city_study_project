from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import engine, Base, AsyncSessionLocal
from .routers import environment
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаем все таблицы при запуске приложения
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed(session)

    yield  # Приложение работает

    # Очищаем соединения при завершении
    await engine.dispose()


app = FastAPI(title="Environment Service", lifespan=lifespan)

app.include_router(environment.router)