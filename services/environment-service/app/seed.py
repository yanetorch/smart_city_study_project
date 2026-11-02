"""Тестовые данные для Environment Service (координаты и локации — Иркутск)."""
import logging
from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.models import Sensor, SensorData

log = logging.getLogger(settings.SERVICE_NAME)

SENSORS = [
    # name, location, sensor_type
    ("Датчик температуры #1", "ул. Карла Маркса, 1 (ИГУ)", "temperature"),
    ("Датчик качества воздуха", "ул. Чкалова, 1 (Центральный рынок)", "air_quality"),
    ("Датчик уровня шума", "ул. Байкальская, 100", "noise"),
    ("Датчик влажности", "ул. Ленина, 15", "humidity"),
]


async def seed(session: AsyncSession) -> None:
    # Проверяем, пуста ли таблица датчиков
    if await session.scalar(select(func.count()).select_from(Sensor)) == 0:
        # Создаем датчики
        sensors_to_add = [
            Sensor(name=name, location=loc, sensor_type=stype)
            for name, loc, stype in SENSORS
        ]
        session.add_all(sensors_to_add)
        await session.commit()  # Коммитим, чтобы получить ID для привязки данных

        log.info("Seeded %s sensors", len(sensors_to_add))

        # Добавляем немного исторических данных для первого датчика (ID = 1)
        if sensors_to_add:
            first_sensor_id = sensors_to_add[0].id
            initial_data = [
                SensorData(sensor_id=first_sensor_id, value=22.5, timestamp=datetime.utcnow() - timedelta(hours=2)),
                SensorData(sensor_id=first_sensor_id, value=23.1, timestamp=datetime.utcnow() - timedelta(hours=1)),
                SensorData(sensor_id=first_sensor_id, value=24.0, timestamp=datetime.utcnow()),
            ]
            session.add_all(initial_data)
            await session.commit()
            log.info("Seeded initial sensor data for sensor ID %s", first_sensor_id)