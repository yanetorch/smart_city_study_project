from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Vehicle(Base):
    #Штука общественного транспорта с текущими координатами

    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_type: Mapped[str] = mapped_column(String(20), index=True)  
    route_number: Mapped[str] = mapped_column(String(10))
    plate_number: Mapped[str] = mapped_column(String(20), unique=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="active")  
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Parking(Base):
    __tablename__ = "parkings"
    __table_args__ = (
        CheckConstraint("total_spots > 0", name="ck_parkings_total_spots_positive"),
        CheckConstraint("price_per_hour >= 0", name="ck_parkings_price_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    total_spots: Mapped[int] = mapped_column(Integer)
    price_per_hour: Mapped[Decimal] = mapped_column(Numeric(10, 2))

    reservations: Mapped[list["ParkingReservation"]] = relationship(back_populates="parking")


class ParkingReservation(Base):
    __tablename__ = "parking_reservations"
    __table_args__ = (CheckConstraint("end_time > start_time", name="ck_reservation_time_range"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    parking_id: Mapped[int] = mapped_column(ForeignKey("parkings.id", ondelete="CASCADE"), index=True)
    # id пользователя из Identity & Auth Service. Внешнего ключа нет — это другая БД.
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    car_number: Mapped[str] = mapped_column(String(20))
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default="active")  # active / cancelled
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    parking: Mapped[Parking] = relationship(back_populates="reservations")
