"""Тестовые данные для Billing Service (счета для тестовых пользователей)."""
import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Invoice, InvoiceStatus

log = logging.getLogger(settings.SERVICE_NAME)

# Тестовые счета (user_id здесь - это username, как мы договорились ранее)
INVOICES = [
    # username, amount, status
    ("testuser", 1500.00, InvoiceStatus.PENDING),
    ("testuser", 3200.50, InvoiceStatus.PAID),
    ("admin", 5000.00, InvoiceStatus.PENDING),
    ("testuser", 450.00, InvoiceStatus.PENDING),
]

async def seed(session: AsyncSession) -> None:
    # Проверяем, пуста ли таблица счетов
    if await session.scalar(select(func.count()).select_from(Invoice)) == 0:
        invoices_to_add = [
            Invoice(user_id=user_id, amount=amount, status=status)
            for user_id, amount, status in INVOICES
        ]
        session.add_all(invoices_to_add)
        await session.commit()
        log.info("Seeded %s invoices", len(invoices_to_add))