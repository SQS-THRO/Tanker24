import json
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.models import Car, HistoryRecord, FuelType, User
from app.routers.export import get_user_data_as_json, get_user_data_as_csv
from app.services.export_data_service import NestedExportDataService, FlatExportDataService


# Helper class for the db mock
class FakeScalarResult:
	def __init__(self, items):
		self._items = items

	def all(self):
		return self._items


# Helper class for the db mock
class FakeExecuteResult:
	def __init__(self, items):
		self._items = items

	def scalars(self):
		return FakeScalarResult(self._items)


class TestExportDataService:
	@pytest.mark.asyncio
	async def test_get_user_data_nested_list_successful(self):
		user = User(id=1)

		car1 = Car(
			id=10,
			owner_id=1,
			type="Limousine",
			license_plate_number="RO-AB-123",
		)
		car2 = Car(
			id=11,
			owner_id=1,
			type="SUV",
			license_plate_number="M-XY-999",
		)

		record1 = HistoryRecord(
			id=100,
			car_id=10,
			timestamp="2026-03-01T10:00:00",
			mileage=50000,
			price_per_litre=1.80,
			litres=40,
			fuel_type=FuelType(name="Diesel"),
		)
		record2 = HistoryRecord(
			id=101,
			car_id=10,
			timestamp="2026-03-15T12:00:00",
			mileage=50500,
			price_per_litre=1.90,
			litres=35,
			fuel_type=FuelType(name="Diesel"),
		)
		record3 = HistoryRecord(
			id=102,
			car_id=11,
			timestamp="2026-03-20T09:30:00",
			mileage=12000,
			price_per_litre=1.85,
			litres=30,
			fuel_type=FuelType(name="E5"),
		)

		db = AsyncMock()
		# Note for learning: everytime the db.execute function is called the next entry from the side_effect
		# list is returned. This is such a nice feature for easy mocking! I love it!
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car1, car2]),
				FakeExecuteResult([record1, record2]),  # history for car1
				FakeExecuteResult([record3]),  # history for car2
			]
		)

		service = NestedExportDataService(db)

		# Call the function under test
		result = await service.get_user_data(user.id)

		# Check if the fields are parsed correctly from the database fields
		assert len(result) == 2

		assert result[0]["id"] == 10
		assert result[0]["type"] == "Limousine"
		assert result[0]["license_plate_number"] == "RO-AB-123"
		assert len(result[0]["history"]) == 2

		# Check datagrams
		assert result[0]["history"][0] == {
			"id": 100,
			"car_id": 10,
			"created_at": "2026-03-01T10:00:00",
			"mileage": 50000,
			"price_per_litre": 1.80,
			"litres": 40,
			"total_price": 72.0,
			"fuel_type": "Diesel",
		}

		assert pytest.approx(result[0]["history"][1]["total_price"]) == pytest.approx(66.5)
		assert result[1]["history"][0]["fuel_type"] == "E5"

	@pytest.mark.asyncio
	async def test_get_user_data_nested_list_empty_history(self):
		user = User(id=1)

		car = Car(
			id=20,
			owner_id=1,
			type="Kombi",
			license_plate_number="MUC-CD-456",
		)

		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),  # Car query
				FakeExecuteResult([]),  # History query for this car is empty
			]
		)

		service = NestedExportDataService(db)
		result = await service.get_user_data(user.id)

		# Check if the history is really empty
		assert result == [
			{
				"id": 20,
				"type": "Kombi",
				"license_plate_number": "MUC-CD-456",
				"history": [],
			}
		]

	@pytest.mark.asyncio
	async def test_get_user_data_nested_list__no_cars(self):
		user = User(id=1)

		db = AsyncMock()
		# db query will return nothing
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([]),
			]
		)

		service = NestedExportDataService(db)
		result = await service.get_user_data(user.id)

		# Check the array is empty for real
		assert result == []

	@pytest.mark.asyncio
	async def test_get_user_data_nested_list_multiple_cars(self):
		user = User(id=1)

		car1 = Car(id=1, owner_id=1, type="Kombi", license_plate_number="MÜB-DF-7777")
		car2 = Car(id=2, owner_id=1, type="SUV", license_plate_number="HO-LE-123")

		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car1, car2]),
				FakeExecuteResult([]),
				FakeExecuteResult([]),
			]
		)

		service = NestedExportDataService(db)
		result = await service.get_user_data(user.id)

		assert len(result) == 2
		assert db.execute.await_count == 3

	@pytest.mark.asyncio
	async def test_get_user_data_nested_list_db_failure_(self):
		user = User(id=1)

		db = AsyncMock()
		# mock a db exception to test the try catch
		db.execute = AsyncMock(side_effect=SQLAlchemyError("The database encountered an error."))
		db.rollback = AsyncMock()

		service = NestedExportDataService(db)

		with pytest.raises(HTTPException) as exc_info:
			await service.get_user_data(user.id)

		# Check the exception returned by the endpoint
		assert exc_info.value.status_code == 503
		assert exc_info.value.detail == "Database temporarily unavailable."

	@pytest.mark.asyncio
	async def test_get_user_data_as_flat_list_successful(self):
		user = User(id=1)

		car = Car(
			id=10,
			owner_id=1,
			type="Limousine",
			license_plate_number="RO-AB-123",
		)

		record = HistoryRecord(
			id=100,
			car_id=10,
			timestamp="2026-03-01T10:00:00",
			mileage=50000,
			price_per_litre=1.8,
			litres=40,
			fuel_type=FuelType(name="Diesel"),
		)

		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),
				FakeExecuteResult([record]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		assert result != []
		assert isinstance(result, list)
		assert len(result) == 1

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_with_no_cars(self):
		user = User(id=1)

		# The user doesn't have any cars
		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		# Check that only the header line is returned
		assert len(result) == 0
		assert result == []

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_skips_cars_without_history(self):
		user = User(id=1)

		car = Car(
			id=30,
			owner_id=1,
			type="Kombi",
			license_plate_number="MUC-CD-456",
		)

		db = AsyncMock()
		# The user registered a car but didn't add any history records yet
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),
				FakeExecuteResult([]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		assert len(result) == 0
		assert "Kombi" not in result
		assert "MUC-CD-456" not in result

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_multiple_history_records_success(self):
		user = User(id=1)

		car = Car(
			id=40,
			owner_id=1,
			type="Limousine",
			license_plate_number="WUN-AA-111",
		)

		record1 = HistoryRecord(
			id=301,
			car_id=40,
			timestamp="2026-01-01T09:00:00",
			mileage=10000,
			price_per_litre=1.7,
			litres=20,
			fuel_type=FuelType(name="Diesel"),
		)

		record2 = HistoryRecord(
			id=302,
			car_id=40,
			timestamp="2026-02-01T09:00:00",
			mileage=11000,
			price_per_litre=1.8,
			litres=25,
			fuel_type=FuelType(name="Diesel"),
		)

		db = AsyncMock()
		# The user has 1 car with multiple history records
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),
				FakeExecuteResult([record1, record2]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		assert len(result) == 2
		assert result[0]["car_id"] == 40
		assert result[0]["license_plate_number"] == "WUN-AA-111"
		assert result[0]["mileage"] == 10000
		assert pytest.approx(result[0]["price_per_litre"]) == pytest.approx(1.7)
		assert result[0]["fuel_type"] == "Diesel"
		assert result[1]["id"] == 302
		assert result[1]["car_id"] == 40
		assert result[1]["license_plate_number"] == "WUN-AA-111"
		assert result[1]["mileage"] == 11000
		assert pytest.approx(result[1]["price_per_litre"]) == pytest.approx(1.8)
		assert result[1]["fuel_type"] == "Diesel"

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_multiple_cars(self):
		user = User(id=1)

		car1 = Car(
			id=50,
			owner_id=1,
			type="SUV",
			license_plate_number="REH-AU-12",
		)
		car2 = Car(
			id=51,
			owner_id=1,
			type="Schräghecklimousine",
			license_plate_number="REH-AU-13",
		)

		record1 = HistoryRecord(
			id=401,
			car_id=50,
			timestamp="2026-03-01T10:00:00",
			mileage=15000,
			price_per_litre=1.9,
			litres=35,
			fuel_type=FuelType(name="E10"),
		)
		record2 = HistoryRecord(
			id=402,
			car_id=51,
			timestamp="2026-03-02T11:00:00",
			mileage=22000,
			price_per_litre=1.6,
			litres=50,
			fuel_type=FuelType(name="Diesel"),
		)

		db = AsyncMock()
		# The user has two cars with 1 history record each
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car1, car2]),
				FakeExecuteResult([record1]),
				FakeExecuteResult([record2]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		assert len(result) == 2
		assert result[0]["car_id"] == 50
		assert result[0]["license_plate_number"] == "REH-AU-12"
		assert result[1]["car_id"] == 51
		assert result[1]["license_plate_number"] == "REH-AU-13"

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_total_price_calculation(self):
		user = User(id=1)

		car = Car(
			id=60,
			owner_id=1,
			type="Kleinbus",
			license_plate_number="RO-LS-333",
		)

		record = HistoryRecord(
			id=500,
			car_id=60,
			timestamp="2026-03-15T14:30:00",
			mileage=80000,
			price_per_litre=1.234,
			litres=12.5,
			fuel_type=FuelType(name="Diesel"),
		)

		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),
				FakeExecuteResult([record]),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)
		result = await service.get_user_data(user.id)

		assert pytest.approx(result[0]["total_price"]) == pytest.approx(15.425)

	@pytest.mark.asyncio
	async def test_get_user_data_flat_list_db_error(self):
		user = User(id=1)

		car = Car(
			id=70,
			owner_id=1,
			type="Kleinbus",
			license_plate_number="RO-LS-333",
		)

		db = AsyncMock()
		# Mock an database exception
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([car]),
				SQLAlchemyError("The database encountered an error."),
			]
		)
		db.rollback = AsyncMock()

		service = FlatExportDataService(db)

		with pytest.raises(HTTPException) as exc_info:
			await service.get_user_data(user.id)

		assert exc_info.value.status_code == 503
		assert exc_info.value.detail == "Database temporarily unavailable."
