import asyncio
import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

log = logging.getLogger(settings.SERVICE_NAME)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_db(retries: int = 10, delay: float = 2.0) -> None:
    """Создаёт таблицы. Postgres может стартовать дольше сервиса — поэтому ретраи."""
    for attempt in range(1, retries + 1):
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            log.info("Database is ready")
            return
        except Exception as e:  # connection refused, "database system is starting up" и т.п.
            log.warning("Database not ready (attempt %s/%s): %s", attempt, retries, e)
            await asyncio.sleep(delay)
    raise RuntimeError("Could not connect to database")
