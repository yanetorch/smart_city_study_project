from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db
from ..models import Sensor, SensorData
from app.dependencies import get_current_user
from app.schemas import *
from datetime import datetime

router = APIRouter(prefix="/sensors", tags=["sensors"])

@router.get("", response_model=list[SensorOut])
async def get_sensors(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Sensor))
    return result.scalars().all()

@router.get("/{sensor_id}/data")
async def get_sensor_data(sensor_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(SensorData).where(SensorData.sensor_id == sensor_id))
    return result.scalars().all()


@router.post("", status_code=201)
async def create_sensor(sensor: SensorCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    new_sensor = Sensor(
        name=sensor.name,
        location=sensor.location,
        sensor_type=sensor.sensor_type
    )
    db.add(new_sensor)
    await db.commit()
    await db.refresh(new_sensor)
    return new_sensor

@router.post("/data", status_code=201)
async def post_sensor_data(data: SensorDataCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # В реальном проекте здесь может быть проверка, что пользователь имеет право писать в этот датчик
    new_data = SensorData(sensor_id=data.sensor_id, value=data.value, timestamp=datetime.utcnow())
    db.add(new_data)
    await db.commit()
    await db.refresh(new_data)
    return {"message": "Данные успешно сохранены", "data": new_data}