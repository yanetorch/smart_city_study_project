from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Invoice, Payment, InvoiceStatus
from ..auth import get_current_user, verify_internal_api_key
from pydantic import BaseModel

router = APIRouter()


class PaymentCreate(BaseModel):
    invoice_id: int
    amount: float


@router.get("/accounts/{username}/invoices")
async def get_invoices(
        username: str,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # 1. Проверка прав: пользователь может смотреть только свои счета
    if current_user["username"] != username:
        raise HTTPException(status_code=403, detail="Доступ к чужим счетам запрещен")

    # 2. Ищем счета по username (исправленная переменная!)
    result = await db.execute(select(Invoice).where(Invoice.user_id == username))
    return result.scalars().all()


@router.post("/payments", status_code=201)
async def create_payment(
        payment: PaymentCreate,
        db: AsyncSession = Depends(get_db),
        current_user: dict = Depends(get_current_user)
):
    # 1. Ищем счет по ID
    result = await db.execute(select(Invoice).where(Invoice.id == payment.invoice_id))
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(status_code=404, detail="Счет не найден")

    # 2. Проверка: нельзя оплатить чужой счет (сравниваем username)
    if invoice.user_id != current_user["username"]:
        raise HTTPException(status_code=403, detail="Нельзя оплатить чужой счет")

    if invoice.status == InvoiceStatus.PAID:
        raise HTTPException(status_code=400, detail="Счет уже оплачен")

    # 3. Создаем платеж и обновляем статус счета
    new_payment = Payment(invoice_id=payment.invoice_id, amount=payment.amount)
    invoice.status = InvoiceStatus.PAID

    db.add(new_payment)
    await db.commit()
    return {"message": "Платеж успешно проведен", "payment_id": new_payment.id}


@router.post("/payments/webhook/success")
async def payment_webhook(
        invoice_id: int,
        db: AsyncSession = Depends(get_db),
        is_internal: bool = Depends(verify_internal_api_key)
):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(status_code=404, detail="Счет не найден")

    invoice.status = InvoiceStatus.PAID
    await db.commit()
    return {"message": "Статус счета обновлен через webhook"}