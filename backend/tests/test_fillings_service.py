# tests/services/test_fillings_service.py

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.exceptions.exceptions import FillingNotFoundException
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

    @pytest.fixture
    def user(self):
        return UserRead(
            id=123,
            email="test@test.com",
            username="testuser",
            is_active=True,
        )

    @pytest.fixture
    def filling(self):
        return FillingDTO(
            car_type="BMW",
            license_plate_number="RO-AB-123",
            timestamp=datetime.now(UTC),
            mileage=12345.6,
            price_per_litre=1.89,
            litres=42.5,
            fuel_type=FuelType.e5,
        )

    @pytest.fixture
    def saved_car(self):
        return Car(
            id=10,
            owner_id=123,
            type="BMW",
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

        service.fuel_type_repository.get_by_name.return_value = (
            db_fuel_type
        )

        await service.save_history_record(
            filling=filling,
            user=user,
        )

        service.car_repo.insert_car_for_owner.assert_awaited_once()

        _, kwargs = (
            service.car_repo.insert_car_for_owner.call_args
        )

        assert kwargs["owner_id"] == user.id
        assert kwargs["car"].type == filling.car_type

        assert (
            kwargs["car"].license_plate_number
            == filling.license_plate_number
        )

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

        service.fuel_type_repository.get_by_name.return_value = (
            db_fuel_type
        )

        await service.save_history_record(
            filling=filling,
            user=user,
        )

        service.fuel_type_repository.get_by_name.assert_awaited_once_with(
            filling.fuel_type
        )

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

        service.fuel_type_repository.get_by_name.return_value = (
            db_fuel_type
        )

        await service.save_history_record(
            filling=filling,
            user=user,
        )

        service.history_repo.insert_history_record.assert_awaited_once()

        history_record = (
            service.history_repo.insert_history_record.call_args.args[0]
        )

        assert history_record.timestamp == filling.timestamp
        assert history_record.mileage == filling.mileage

        assert (
            history_record.price_per_litre
            == filling.price_per_litre
        )

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

        assert (
            str(exc_info.value)
            == "Filling with ID 99 not found"
        )