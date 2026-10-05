from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IssueCategory(str, Enum):
    water = "water"              # водоснабжение
    heating = "heating"          # отопление
    electricity = "electricity"  # электричество
    gas = "gas"                  # газ
    garbage = "garbage"          # вывоз мусора
    roads = "roads"              # дворы, дороги
    other = "other"


class IssueStatus(str, Enum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"
    rejected = "rejected"


# из финальных статусов заявку уже не перевести
FINAL_STATUSES = {IssueStatus.resolved.value, IssueStatus.rejected.value}


class IssueCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200, examples=["Нет горячей воды"])
    description: str = Field(min_length=1, max_length=5000, examples=["Со вчерашнего вечера нет горячей воды во всём подъезде"])
    address: str = Field(min_length=3, max_length=255, examples=["ул. Ленина, 5, кв. 12"])
    category: IssueCategory


class IssueUpdate(BaseModel):
    status: IssueStatus
    comment: str | None = Field(default=None, max_length=2000, examples=["Бригада выехала"])


class StatusHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    old_status: str | None
    new_status: str
    changed_by: int
    comment: str | None
    changed_at: datetime


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    description: str
    address: str
    category: str
    status: str
    created_at: datetime
    updated_at: datetime


class IssueDetailOut(IssueOut):
    history: list[StatusHistoryOut]
