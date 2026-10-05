from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class VehicleType(str, Enum):
    bus = "bus"
    tram = "tram"
    trolleybus = "trolleybus"


class VehicleStatus(str, Enum):
    active = "active"
    in_depot = "in_depot"
    maintenance = "maintenance"


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_type: str
    route_number: str
    plate_number: str
    latitude: float
    longitude: float
    status: str
    updated_at: datetime


class ParkingOut(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    total_spots: int
    free_spots: int  
    price_per_hour: Decimal


class ReservationCreate(BaseModel):
    car_number: str = Field(min_length=1, max_length=20, examples=["А123ВС38"])
    start_time: datetime | None = Field(default=None, description="Начало брони (ISO 8601). По умолчанию — сейчас")
    hours: int = Field(ge=1, le=24, description="Длительность в часах")


class ReservationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    parking_id: int
    user_id: int
    car_number: str
    start_time: datetime
    end_time: datetime
    total_price: Decimal
    status: str
    created_at: datetime
