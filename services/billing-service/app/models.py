from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
# from sqlalchemy.orm import declarative_base
from datetime import datetime
from .database import Base
import enum



class InvoiceStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"

class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    # username = Column(String, index=True)
    amount = Column(Float)
    status = Column(String, default=InvoiceStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    amount = Column(Float)
    status = Column(String, default="success")
    created_at = Column(DateTime, default=datetime.utcnow)