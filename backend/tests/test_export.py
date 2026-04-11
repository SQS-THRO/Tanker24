import json
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.models import Car, HistoryRecord, FuelType, User
from app.routers.export import get_user_data_as_json, get_user_data_as_csv


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


class TestExportEndpoint:
	@pytest.mark.asyncio
	async def test_get_user_data_successful(self):
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

		# Call the function under test
		response = await get_user_data_as_json(db=db, user=user)
		data = json.loads(response.body.decode())

		# Check if the fields are parsed correctly from the database fields
		assert len(data) == 2

		assert data[0]["id"] == 10
		assert data[0]["type"] == "Limousine"
		assert data[0]["license_plate_number"] == "RO-AB-123"
		assert len(data[0]["history"]) == 2

		# Check datagrams
		assert data[0]["history"][0] == {
			"id": 100,
			"car_id": 10,
			"created_at": "2026-03-01T10:00:00",
			"mileage": 50000,
			"price_per_litre": 1.80,
			"litres": 40,
			"total_price": 72.0,
			"fuel_type": "Diesel",
		}

		assert pytest.approx(data[0]["history"][1]["total_price"]) == pytest.approx(66.5)
		assert data[1]["history"][0]["fuel_type"] == "E5"

	@pytest.mark.asyncio
	async def test_get_user_data_empty_history(self):
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

		# Call the function for getting the user data. It should not throw an exception
		# as empty histories are handled gracefully.
		response = await get_user_data_as_json(db=db, user=user)

		data = json.loads(response.body.decode())

		# Check if the history is really empty
		assert data == [
			{
				"id": 20,
				"type": "Kombi",
				"license_plate_number": "MUC-CD-456",
				"history": [],
			}
		]

	@pytest.mark.asyncio
	async def test_get_user_data_no_cars(self):
		user = User(id=1)

		db = AsyncMock()
		# db query will return nothing
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([]),
			]
		)

		response = await get_user_data_as_json(db=db, user=user)
		data = json.loads(response.body.decode())

		# Check the array is empty for real
		assert data == []

	@pytest.mark.asyncio
	async def test_get_user_data_multiple_cars(self):
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

		response = await get_user_data_as_json(db=db, user=user)

		# Check if the response is indeed a JSONResponse and not an exception
		assert isinstance(response, JSONResponse)

		data = json.loads(response.body.decode())

		assert len(data) == 2
		assert db.execute.await_count == 3

	@pytest.mark.asyncio
	async def test_get_user_data_db_failure_(self):
		user = User(id=1)

		db = AsyncMock()
		# mock a db exception to test the try catch
		db.execute = AsyncMock(side_effect=SQLAlchemyError("The database encountered an error."))
		db.rollback = AsyncMock()

		with pytest.raises(HTTPException) as exc_info:
			await get_user_data_as_json(db=db, user=user)

		# Check the exception returned by the endpoint
		assert exc_info.value.status_code == 503
		assert exc_info.value.detail == "Database temporarily unavailable."

	# Helper method for consuming csv files to validate the responses
	async def read_streaming_response_body(self, response) -> str:
		body = ""
		async for chunk in response.body_iterator:
			if isinstance(chunk, bytes):
				body += chunk.decode("utf-8")
			else:
				body += chunk
		return body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_successful(self):
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

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		expected_header = (
			"id;car_id;car_type;license_plate_number;created_at;mileage;price_per_litre;litres;total_price;fuel_type"
		)
		expected_row = "100;10;Limousine;RO-AB-123;2026-03-01T10:00:00;50000;1.8;40;72.0;Diesel"

		# Compare response fields
		assert response.media_type == "text/csv"
		assert response.headers["content-disposition"] == "attachment; filename=car_history_data.csv"
		assert expected_header in body
		assert expected_row in body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_with_no_cars(self):
		user = User(id=1)

		# The user doesn't have any cars
		db = AsyncMock()
		db.execute = AsyncMock(
			side_effect=[
				FakeExecuteResult([]),
			]
		)
		db.rollback = AsyncMock()

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		lines = body.splitlines()

		# Check that only the header line is returned
		assert len(lines) == 1
		assert (
			lines[0]
			== "id;car_id;car_type;license_plate_number;created_at;mileage;price_per_litre;litres;total_price;fuel_type"
		)

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_skips_cars_without_history(self):
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

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		lines = body.splitlines()

		# The csv should only include the header line as there are no history records
		assert len(lines) == 1
		assert "Kombi" not in body
		assert "MUC-CD-456" not in body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_multiple_history_records_success(self):
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

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		lines = body.splitlines()

		# The csv should have 3 lines. 1 Header and 2 data rows
		assert len(lines) == 3
		assert "301;40;Limousine;WUN-AA-111;2026-01-01T09:00:00;10000;1.7;20;34.0;Diesel" in body
		assert "302;40;Limousine;WUN-AA-111;2026-02-01T09:00:00;11000;1.8;25;45.0;Diesel" in body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_multiple_cars(self):
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

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		assert "401;50;SUV;REH-AU-12;2026-03-01T10:00:00;15000;1.9;35;66.5;E10" in body
		assert "402;51;Schräghecklimousine;REH-AU-13;2026-03-02T11:00:00;22000;1.6;50;80.0;Diesel" in body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_total_price_calculation(self):
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

		response = await get_user_data_as_csv(db=db, user=user)
		body = await self.read_streaming_response_body(response)

		assert "15.425" in body

	@pytest.mark.asyncio
	async def test_get_user_data_as_csv_db_error(self):
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

		with pytest.raises(HTTPException) as exc_info:
			await get_user_data_as_csv(db=db, user=user)

		assert exc_info.value.status_code == 503
		assert exc_info.value.detail == "Database temporarily unavailable."
