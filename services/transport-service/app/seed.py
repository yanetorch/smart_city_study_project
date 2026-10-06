"""Тестовые данные, чтобы на демонстрации списки не были пустыми (координаты — Иркутск)."""
import logging
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Parking, Vehicle

log = logging.getLogger(settings.SERVICE_NAME)

VEHICLES = [
    # type, route, plate, lat, lon, status
    ("bus", "20", "А101АА38", 52.2869, 104.2810, "active"),
    ("bus", "20", "А102АА38", 52.2721, 104.2965, "active"),
    ("bus", "42", "В201ВВ38", 52.2600, 104.3200, "active"),
    ("bus", "80", "Е301ЕЕ38", 52.2510, 104.2650, "in_depot"),
    ("tram", "1", "Т-001", 52.2835, 104.2900, "active"),
    ("tram", "4", "Т-014", 52.2905, 104.2700, "active"),
    ("trolleybus", "3", "ТБ-103", 52.2780, 104.3050, "active"),
    ("trolleybus", "5", "ТБ-205", 52.2650, 104.2850, "maintenance"),
]

PARKINGS = [
    # name, address, lat, lon, spots, price
    ("Парковка у Центрального рынка", "ул. Чкалова, 1", 52.2836, 104.2970, 40, Decimal("60.00")),
    ("Парковка на Карла Маркса", "ул. Карла Маркса, 15", 52.2858, 104.2846, 20, Decimal("80.00")),
    ("Парковка у ИГУ", "ул. Карла Маркса, 1", 52.2805, 104.2795, 15, Decimal("50.00")),
    ("Парковка у ж/д вокзала", "ул. Челнокова, 1", 52.2735, 104.2580, 5, Decimal("100.00")),
]


async def seed(session: AsyncSession) -> None:
    if await session.scalar(select(func.count()).select_from(Vehicle)) == 0:
        session.add_all(
            Vehicle(vehicle_type=t, route_number=r, plate_number=p, latitude=la, longitude=lo, status=s)
            for t, r, p, la, lo, s in VEHICLES
        )
        log.info("Seeded %s vehicles", len(VEHICLES))

    if await session.scalar(select(func.count()).select_from(Parking)) == 0:
        session.add_all(
            Parking(name=n, address=a, latitude=la, longitude=lo, total_spots=s, price_per_hour=pr)
            for n, a, la, lo, s, pr in PARKINGS
        )
        log.info("Seeded %s parkings", len(PARKINGS))

    await session.commit()
