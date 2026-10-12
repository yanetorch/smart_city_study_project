import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import CurrentUser, get_current_user
from app.models import Parking, ParkingReservation
from app.notifications import send_notification
from app.schemas import ParkingOut, ReservationCreate, ReservationOut

log = logging.getLogger(settings.SERVICE_NAME)

router = APIRouter(prefix="/parking", tags=["parking"])


def _busy_now_subquery():
    """Сколько мест на каждой парковке занято бронями прямо сейчас."""
    now = func.now()
    return (
        select(ParkingReservation.parking_id, func.count().label("busy"))
        .where(
            ParkingReservation.status == "active",
            ParkingReservation.start_time <= now,
            ParkingReservation.end_time > now,
        )
        .group_by(ParkingReservation.parking_id)
        .subquery()
    )


def _to_out(parking: Parking, busy: int) -> ParkingOut:
    return ParkingOut(
        id=parking.id,
        name=parking.name,
        address=parking.address,
        latitude=parking.latitude,
        longitude=parking.longitude,
        total_spots=parking.total_spots,
        free_spots=max(parking.total_spots - busy, 0),
        price_per_hour=parking.price_per_hour,
    )


@router.get("", response_model=list[ParkingOut])
async def list_parkings(db: AsyncSession = Depends(get_db)):
    """Информация о парковках, включая количество свободных мест."""
    busy = _busy_now_subquery()
    stmt = (
        select(Parking, func.coalesce(busy.c.busy, 0))
        .outerjoin(busy, busy.c.parking_id == Parking.id)
        .order_by(Parking.id)
    )
    result = await db.execute(stmt)
    return [_to_out(p, b) for p, b in result.all()]


@router.get("/{parking_id}", response_model=ParkingOut)
async def get_parking(parking_id: int, db: AsyncSession = Depends(get_db)):
    busy = _busy_now_subquery()
    stmt = (
        select(Parking, func.coalesce(busy.c.busy, 0))
        .outerjoin(busy, busy.c.parking_id == Parking.id)
        .where(Parking.id == parking_id)
    )
    row = (await db.execute(stmt)).first()
    if row is None:
        raise HTTPException(404, "Parking not found")
    return _to_out(*row)


@router.post("/{parking_id}/reserve", response_model=ReservationOut, status_code=status.HTTP_201_CREATED)
async def reserve_spot(
    parking_id: int,
    data: ReservationCreate,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Бронирование парковочного места (нужен JWT)."""
    now = datetime.now(timezone.utc)
    start = data.start_time or now
    if start.tzinfo is None:  # время без часового пояса считаем UTC
        start = start.replace(tzinfo=timezone.utc)
    if start < now - timedelta(minutes=5):
        raise HTTPException(400, "Start time is in the past")
    end = start + timedelta(hours=data.hours)

    # SELECT ... FOR UPDATE: блокируем строку парковки, чтобы два параллельных
    # запроса не заняли последнее место одновременно
    parking = await db.get(Parking, parking_id, with_for_update=True)
    if parking is None:
        raise HTTPException(404, "Parking not found")

    overlapping = await db.scalar(
        select(func.count())
        .select_from(ParkingReservation)
        .where(
            ParkingReservation.parking_id == parking_id,
            ParkingReservation.status == "active",
            ParkingReservation.start_time < end,
            ParkingReservation.end_time > start,
        )
    )
    if overlapping >= parking.total_spots:
        log.info("Reservation rejected: parking %s is full for %s - %s", parking_id, start, end)
        raise HTTPException(409, "No free spots for the selected time")

    reservation = ParkingReservation(
        parking_id=parking_id,
        user_id=user.id,
        car_number=data.car_number.upper(),
        start_time=start,
        end_time=end,
        total_price=parking.price_per_hour * data.hours,
        status="active",
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    log.info(
        "Reservation %s created: user=%s parking=%s car=%s %s - %s",
        reservation.id, user.id, parking_id, reservation.car_number, start, end,
    )
    await send_notification(
        user.id,
        "Парковка забронирована",
        f"{parking.name}: место забронировано с {start:%d.%m %H:%M} до {end:%d.%m %H:%M} (UTC), "
        f"стоимость {reservation.total_price} руб.",
    )
    return reservation
