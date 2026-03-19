from __future__ import annotations
from app.schemas.history_record import HistoryRecord

from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    type: str
    license_plate_number: str


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    type: str | None = None
    license_plate_number: str | None = None


class Car(CarBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class CarWithHistory(Car):
    history_records: list[HistoryRecord] = []


