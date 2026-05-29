# tests/services/test_fillings_service.py
from unittest.mock import AsyncMock, Mock

import pytest

from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.exceptions.exceptions import FillingNotFoundException
from app.schemas import HistoryRecord
from app.schemas.car import Car
from app.schemas.user import UserRead
from app.services.fillings_service import FillingsService


class TestFillingsService:
	@pytest.fixture
	def service(self):
		service = FillingsService(db=AsyncMock())

		service.car_repo = AsyncMock()
		service.history_repo = AsyncMock()
		service.fuel_type_repository = AsyncMock()

		return service

	TEST_PASSWORD = "test-password"  # NO SONAR

	@pytest.fixture
	def user(self) -> UserRead:
		return UserRead(
			id=123,
			email="max@Tanker24.eu",
			forename="Max",
			surname="Musterfrau",
			is_active=True,
			is_superuser=False,
			is_verified=True,
			hashed_password=self.TEST_PASSWORD,
		)

	@pytest.fixture
	def filling(self):
		return FillingDTO(
			car_type="Limousine",
			license_plate_number="RO-AB-123",
			timestamp="2026-05-23T10:25:31.482193+00:00",
			mileage=12345.6,
			price_per_litre=1.89,
			litres=42.5,
			tankerkoenig_station_id="213215465123153465123135131",
			fuel_type=FuelType.e5,
		)

	@pytest.fixture
	def saved_car(self):
		return Car(
			id=10,
			owner_id=123,
			type="Limousine",
			license_plate_number="RO-AB-123",
		)

	@pytest.fixture
	def db_fuel_type(self):
		class FuelTypeDbObject:
			def __init__(self):
				self.id = 2

		return FuelTypeDbObject()

	@pytest.mark.asyncio
	async def test_save_history_record_creates_car_for_user(
		self,
		service,
		filling,
		user,
		saved_car,
		db_fuel_type,
	):
		service.car_repo.insert_car_for_owner.return_value = saved_car

		service.fuel_type_repository.get_by_name.return_value = db_fuel_type

		await service.save_history_record(
			filling=filling,
			user=user,
		)

		service.car_repo.insert_car_for_owner.assert_awaited_once()

		_, kwargs = service.car_repo.insert_car_for_owner.call_args

		assert kwargs["owner_id"] == user.id
		assert kwargs["car"].type == filling.car_type

		assert kwargs["car"].license_plate_number == filling.license_plate_number

	@pytest.mark.asyncio
	async def test_save_history_record_resolves_fuel_type(
		self,
		service,
		filling,
		user,
		saved_car,
		db_fuel_type,
	):
		service.car_repo.insert_car_for_owner.return_value = saved_car

		service.fuel_type_repository.get_by_name.return_value = db_fuel_type

		await service.save_history_record(
			filling=filling,
			user=user,
		)

		service.fuel_type_repository.get_by_name.assert_awaited_once_with(filling.fuel_type)

	@pytest.mark.asyncio
	async def test_save_history_record_inserts_history_record(
		self,
		service,
		filling,
		user,
		saved_car,
		db_fuel_type,
	):
		service.car_repo.insert_car_for_owner.return_value = saved_car

		service.fuel_type_repository.get_by_name.return_value = db_fuel_type

		await service.save_history_record(
			filling=filling,
			user=user,
		)

		service.history_repo.insert_history_record.assert_awaited_once()

		history_record = service.history_repo.insert_history_record.call_args.args[0]

		assert history_record.timestamp == filling.timestamp
		assert history_record.mileage == filling.mileage

		assert history_record.price_per_litre == filling.price_per_litre

		assert history_record.litres == filling.litres
		assert history_record.car_id == saved_car.id
		assert history_record.fuel_type_id == db_fuel_type.id

	@pytest.mark.asyncio
	async def test_delete_history_record_deletes_for_authenticated_user(
		self,
		service,
		user,
	):
		service.history_repo.delete_by_id_for_user.return_value = True

		await service.delete_history_record(
			history_record_id=99,
			user=user,
		)

		service.history_repo.delete_by_id_for_user.assert_awaited_once_with(
			history_record_id=99,
			user_id=user.id,
		)

	@pytest.mark.asyncio
	async def test_delete_history_record_raises_when_not_found(
		self,
		service,
		user,
	):
		service.history_repo.delete_by_id_for_user.return_value = False

		with pytest.raises(FillingNotFoundException) as exc_info:
			await service.delete_history_record(
				history_record_id=99,
				user=user,
			)

		assert exc_info.value.filling_id == 99

		assert str(exc_info.value) == "Filling with ID 99 not found"

	@pytest.mark.asyncio
	async def test_get_history_records_for_user_returns_records_for_all_user_cars(
		self,
		user: UserRead,
	) -> None:
		service = FillingsService(db=AsyncMock())

		car1 = Car(
			id=50,
			owner_id=user.id,
			type="SUV",
			license_plate_number="REH-AU-12",
		)
		car2 = Car(
			id=51,
			owner_id=user.id,
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
			fuel_type_id=1,
			tankerkoenig_station_id="ABC123454789",
		)
		record2 = HistoryRecord(
			id=402,
			car_id=51,
			timestamp="2026-03-02T11:00:00",
			mileage=22000,
			price_per_litre=1.6,
			litres=50,
			fuel_type_id=2,
			tankerkoenig_station_id="ABC123454789",
		)

		service.car_repo = Mock()
		service.car_repo.get_cars_by_owner = AsyncMock(return_value=[car1, car2])

		service.history_repo = Mock()
		service.history_repo.get_history_records_by_car = AsyncMock(
			side_effect=[
				[record1],
				[record2],
			]
		)

		result = await service.get_filling_dto_for_user(user=user)

		assert len(result) == 2
		assert result[0].id == record1.id
		assert result[1].id == record2.id
		assert result[0].car_id == record1.car_id
		assert result[1].car_id == record2.car_id

		service.car_repo.get_cars_by_owner.assert_awaited_once_with(user.id)

		service.history_repo.get_history_records_by_car.assert_any_await(50)
		service.history_repo.get_history_records_by_car.assert_any_await(51)

		assert service.history_repo.get_history_records_by_car.await_count == 2
