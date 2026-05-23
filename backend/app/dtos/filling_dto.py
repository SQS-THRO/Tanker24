from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel

from build.lib.app.models import FuelType


@dataclass
class FillingDTO(BaseModel):
	license_plate_number: str
	car_type: str
	mileage: int
	timestamp: datetime
	price_per_litre: float
	litres: float
	station_id: str
	fuel_type: FuelType
