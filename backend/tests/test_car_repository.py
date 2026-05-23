# tests/repositories/test_car_repository.py

from unittest.mock import AsyncMock, Mock

import pytest

from app.models import Car
from app.repositories.car_repository import CarRepository
from app.schemas.car import CarCreate


class TestCarRepository:
	@pytest.fixture
	def db(self):
		db = Mock()
		db.execute = AsyncMock()
		db.add = Mock()
		db.commit = AsyncMock()
		db.refresh = AsyncMock()
		return db

	@pytest.fixture
	def car_create(self) -> CarCreate:
		return CarCreate(
			type="Limousine",
			license_plate_number="RO-AB-123",
		)

	@pytest.mark.asyncio
	async def test_insert_car_for_owner_returns_existing_car(
		self,
		db,
		car_create: CarCreate,
	) -> None:
		existing_car = Car(
			id=10,
			type="Limousine",
			license_plate_number="RO-AB-123",
			owner_id=123,
		)

		execute_result = Mock()
		execute_result.scalar_one_or_none.return_value = existing_car
		db.execute.return_value = execute_result

		repository = CarRepository(db)

		result = await repository.insert_car_for_owner(
			owner_id=123,
			car=car_create,
		)

		assert result == existing_car
		db.execute.assert_awaited_once()
		execute_result.scalar_one_or_none.assert_called_once()

		db.add.assert_not_called()
		db.commit.assert_not_awaited()
		db.refresh.assert_not_awaited()

	@pytest.mark.asyncio
	async def test_insert_car_for_owner_creates_new_car_when_none_exists(
		self,
		db,
		car_create: CarCreate,
	) -> None:
		execute_result = Mock()
		execute_result.scalar_one_or_none.return_value = None
		db.execute.return_value = execute_result

		repository = CarRepository(db)

		result = await repository.insert_car_for_owner(
			owner_id=123,
			car=car_create,
		)

		db.execute.assert_awaited_once()
		execute_result.scalar_one_or_none.assert_called_once()

		db.add.assert_called_once()
		added_car = db.add.call_args.args[0]

		assert isinstance(added_car, Car)
		assert added_car.type == car_create.type
		assert added_car.license_plate_number == car_create.license_plate_number
		assert added_car.owner_id == 123

		db.commit.assert_awaited_once()
		db.refresh.assert_awaited_once_with(added_car)

		assert result == added_car
