from __future__ import annotations

from typing import TYPE_CHECKING

from app.schemas.fuel_type import FuelType

if TYPE_CHECKING:
    from app.schemas.car import Car

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HistoryRecordBase(BaseModel):
    timestamp: datetime | None = None
    mileage: float
    price_per_litre: float
    litres: float
    car_id: int
    fuel_type_id: int


class HistoryRecordCreate(HistoryRecordBase):
    pass


class HistoryRecordUpdate(BaseModel):
    timestamp: datetime | None = None
    mileage: float | None = None
    price_per_litre: float | None = None
    litres: float | None = None
    car_id: int | None = None
    fuel_type_id: int | None = None


class HistoryRecord(HistoryRecordBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class HistoryRecordWithRelations(HistoryRecord):
    car: Car | None = None
    fuel_type: FuelType | None = None

