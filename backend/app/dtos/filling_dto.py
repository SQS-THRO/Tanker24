from datetime import datetime

from pydantic import BaseModel

from app.dtos.gas_station_dtos import FuelType

class FillingDTO(BaseModel):
	license_plate_number: str
	car_type: str
	mileage: float
	timestamp: datetime
	price_per_litre: float
	litres: float
	tankerkoenig_station_id: str
	fuel_type: FuelType
