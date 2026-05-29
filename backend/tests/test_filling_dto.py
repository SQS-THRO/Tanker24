from datetime import datetime
from types import SimpleNamespace

from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.models import HistoryRecord, Car, FuelType as FuelTypeModel


class TestFillingDTO:
	def test_from_history_record_maps_all_fields_correctly(self):
		timestamp = datetime(2026, 5, 29, 12, 30)

		history_record = HistoryRecord(
			id=1,
			car=Car(
				license_plate_number="RO-AB-123",
				type="SUV",
			),
			mileage=12345.6,
			timestamp=timestamp,
			price_per_litre=1.799,
			litres=45.2,
			tankerkoenig_station_id="station-123",
			fuel_type=FuelTypeModel(
            id = 1,
            name=FuelType.diesel.name,
            ),
		)

		dto = FillingDTO.from_history_record(history_record)

		assert dto.id == 1
		assert dto.license_plate_number == "RO-AB-123"
		assert dto.car_type == "SUV"
		assert dto.mileage == 12345.6
		assert dto.timestamp == timestamp
		assert dto.price_per_litre == 1.799
		assert dto.litres == 45.2
		assert dto.tankerkoenig_station_id == "station-123"
		assert dto.fuel_type == FuelType.diesel
