import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import CurrentUser, get_current_user
from app.models import ParkingReservation
from app.schemas import ReservationOut

log = logging.getLogger(settings.SERVICE_NAME)

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("/my", response_model=list[ReservationOut])
async def my_reservations(user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    #Брони текущего пользователя
    result = await db.execute(
        select(ParkingReservation)
        .where(ParkingReservation.user_id == user.id)
        .order_by(ParkingReservation.start_time.desc())
    )
    return result.scalars().all()


@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
async def cancel_reservation(
    reservation_id: int,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    #Отмена своей брони
    reservation = await db.get(ParkingReservation, reservation_id)
    if reservation is None:
        raise HTTPException(404, "Reservation not found")
    if reservation.user_id != user.id:
        raise HTTPException(403, "This is not your reservation")
    if reservation.status != "active":
        raise HTTPException(409, "Reservation is already cancelled")

    reservation.status = "cancelled"
    await db.commit()
    await db.refresh(reservation)
    log.info("Reservation %s cancelled by user %s", reservation_id, user.id)
    return reservation
