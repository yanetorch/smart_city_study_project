from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# базовый класс
class Base(DeclarativeBase):
    pass

# движок
# echo=True на время дебага
# pool_pre_ping можно поменять на pool_recycle?
engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

# фабрика сессий
# expitre_on_commit=False из-за асинхрона
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# асинхронный генератор
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise