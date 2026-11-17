"""Тестовые данные для Billing Service."""
import logging
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Invoice, InvoiceStatus

log = logging.getLogger(settings.SERVICE_NAME)

# user_id — это id пользователя из auth-service (целое число)
INVOICES = [
    # user_id, amount, status
    (1, 1500.00, InvoiceStatus.PENDING.value),
    (1, 3200.50, InvoiceStatus.PAID.value),
    (2, 5000.00, InvoiceStatus.PENDING.value),
    (1, 450.00, InvoiceStatus.PENDING.value),
]

async def seed(session: AsyncSession) -> None:
    if await session.scalar(select(func.count()).select_from(Invoice)) == 0:
        invoices_to_add = [
            Invoice(user_id=user_id, amount=amount, status=status)
            for user_id, amount, status in INVOICES
        ]
        session.add_all(invoices_to_add)
        await session.commit()
        log.info("Seeded %s invoices", len(invoices_to_add))