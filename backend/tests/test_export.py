import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models import Car, HistoryRecord, FuelType, User
from app.routers.export import get_user_data_as_json


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class FakeExecuteResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return FakeScalarResult(self._items)

class TestExportEndpoint:
    @pytest.mark.asyncio
    async def test_get_user_data_successful(self):
        # Note to self: SimpleNamespace allows us to create objects on the fly.
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
        data = json.loads(response)

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
        data = json.loads(response)

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
        data = json.loads(response)

        # Check the array is empty for real
        assert data == []

    @pytest.mark.asyncio
    async def test_get_user_data_multiple_cars(self):
        user = SimpleNamespace(id=1)

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
        data = json.loads(response)

        assert len(data) == 2
        assert db.execute.await_count == 3

    @pytest.mark.asyncio
    async def test_get_user_data_db_failure_(self):
        user = User(id=1)

        db = AsyncMock()
        # mock a db exception to test the try catch
        db.execute = AsyncMock(side_effect=SQLAlchemyError("DB is down"))
        db.rollback = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await get_user_data_as_json(db=db, user=user)

        # Check the exception returned by the endpoint
        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Database temporarily unavailable."