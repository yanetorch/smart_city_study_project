from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Vehicle
from app.schemas import VehicleOut, VehicleStatus, VehicleType

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleOut])
async def list_vehicles(
    type: VehicleType | None = None,
    route: str | None = None,
    status: VehicleStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    #Список транспорта
    stmt = select(Vehicle).order_by(Vehicle.id)
    if type is not None:
        stmt = stmt.where(Vehicle.vehicle_type == type.value)
    if route is not None:
        stmt = stmt.where(Vehicle.route_number == route)
    if status is not None:
        stmt = stmt.where(Vehicle.status == status.value)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{vehicle_id}", response_model=VehicleOut)
async def get_vehicle(vehicle_id: int, db: AsyncSession = Depends(get_db)):
    vehicle = await db.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise HTTPException(404, "Vehicle not found")
    return vehicle
