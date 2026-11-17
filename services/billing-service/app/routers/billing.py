from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Invoice, Payment, InvoiceStatus
from ..schemas import InvoiceOut, PaymentCreate, PaymentOut
from app.dependencies import CurrentUser, get_current_user

router = APIRouter()

@router.get("/accounts/{user_id}/invoices", response_model=list[InvoiceOut])
async def get_invoices(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    # Пользователь может смотреть только свои счета
    if current_user.id != user_id:
        raise HTTPException(403, "Доступ к чужим счетам запрещен")

    result = await db.execute(
        select(Invoice).where(Invoice.user_id == user_id).order_by(Invoice.id)
    )
    return result.scalars().all()


@router.post("/payments", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    result = await db.execute(
        select(Invoice).where(Invoice.id == payment.invoice_id).with_for_update()
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(404, "Счет не найден")

    if invoice.user_id != current_user.id:
        raise HTTPException(403, "Нельзя оплатить чужой счет")

    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(400, "Счет уже оплачен")

    # Проверка суммы: нельзя оплатить меньше, чем выставлено
    if abs(payment.amount - invoice.amount) > 0.01:
        raise HTTPException(400, "Сумма платежа не совпадает со счетом")

    new_payment = Payment(
        invoice_id=invoice.id,
        user_id=current_user.id,
        amount=payment.amount,
        status="success",
    )
    invoice.status = InvoiceStatus.PAID.value

    db.add(new_payment)
    await db.commit()
    await db.refresh(new_payment)
    return new_payment

# по сути, заглушка (по-хорошему должна быть какая-нибудь проверка подписи)
@router.post("/payments/webhook/success")
async def payment_webhook(invoice_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice:
        raise HTTPException(404, "Счет не найден")
    invoice.status = InvoiceStatus.PAID.value
    await db.commit()
    return {"message": "Статус счета обновлен через webhook"}