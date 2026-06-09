# tests/repositories/test_fuel_type_repository.py

from unittest.mock import AsyncMock, Mock

import pytest

from app.dtos.gas_station_dtos import FuelType
from app.models import FuelType as FuelTypeModel
from app.repositories.fuel_type_repository import FuelTypeRepository


class TestFuelTypeRepository:
	@pytest.fixture
	def db(self):
		db = Mock()
		db.execute = AsyncMock()
		return db

	@pytest.mark.asyncio
	async def test_get_by_name_returns_fuel_type_when_found(self, db) -> None:
		expected_fuel_type = FuelTypeModel(
			id=1,
			name="e5",
		)

		# mock the database response to not break your database
		result = Mock()
		result.scalar_one_or_none.return_value = expected_fuel_type
		db.execute.return_value = result

		repository = FuelTypeRepository(db)

		actual_fuel_type = await repository.get_by_name(FuelType.e5)

		assert actual_fuel_type == expected_fuel_type
		db.execute.assert_awaited_once()
		result.scalar_one_or_none.assert_called_once()

	@pytest.mark.asyncio
	async def test_get_by_name_raises_value_error_when_not_found(self, db) -> None:
		result = Mock()
		result.scalar_one_or_none.return_value = None
		db.execute.return_value = result

		repository = FuelTypeRepository(db)

		with pytest.raises(ValueError) as exc_info:
			await repository.get_by_name(FuelType.e5)

		assert str(exc_info.value) == "Fuel type does not exist: e5"
		db.execute.assert_awaited_once()
		result.scalar_one_or_none.assert_called_once()
