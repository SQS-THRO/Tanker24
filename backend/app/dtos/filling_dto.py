from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.dtos.gas_station_dtos import FuelType
from app.models import HistoryRecord


class FillingDTO(BaseModel):
	license_plate_number: str
	car_type: str
	mileage: float
	timestamp: datetime
	price_per_litre: float
	litres: float
	tankerkoenig_station_id: str
	fuel_type: FuelType
	id: Optional[int]

	@classmethod
	def from_history_record(
			cls,
			history_record: HistoryRecord,
	) -> "FillingDTO":
		return cls(
			id=history_record.id,
			license_plate_number=history_record.car.license_plate_number,
			car_type=history_record.car.type,
			mileage=history_record.mileage,
			timestamp=history_record.timestamp,
			price_per_litre=history_record.price_per_litre,
			litres=history_record.litres,
			tankerkoenig_station_id=history_record.tankerkoenig_station_id,
			fuel_type=history_record.fuel_type.name,
		)