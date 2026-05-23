# tests/routers/test_fillings.py

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth import get_current_active_user
from app.dependencies import get_fillings_service
from app.dtos.gas_station_dtos import FuelType
from app.exceptions.exceptions import FillingNotFoundException
from app.routers.fillings import router
from app.schemas.user import UserRead


class TestFillings:

    @pytest.fixture
    def user(self) -> UserRead:
        return UserRead(
            id=123,
            email="test@test.com",
            username="testuser",
            is_active=True,
        )

    @pytest.fixture
    def service(self):
        service = AsyncMock()
        service.save_history_record = AsyncMock()
        service.delete_history_record = AsyncMock()
        return service

    @pytest.fixture
    def client(self, user, service) -> TestClient:
        app = FastAPI()
        app.include_router(router)

        async def override_current_user():
            return user

        def override_fillings_service():
            return service

        app.dependency_overrides[get_current_active_user] = override_current_user
        app.dependency_overrides[get_fillings_service] = override_fillings_service

        return TestClient(app)

    def test_post_filling_data_returns_200(
        self,
        client: TestClient,
        service,
        user: UserRead,
    ) -> None:
        payload = {
            "car_type": "BMW",
            "license_plate_number": " ro-ab-123 ",
            "timestamp": datetime.now(UTC).isoformat(),
            "mileage": 12345.6,
            "price_per_litre": 1.89,
            "litres": 42.5,
            "fuel_type": FuelType.e5.value,
        }

        response = client.post("/fillings/create", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "Filling stored successfully"}

        service.save_history_record.assert_awaited_once()
        _, kwargs = service.save_history_record.call_args

        assert kwargs["user"] == user
        assert kwargs["filling"].license_plate_number == "RO-AB-123"
        assert kwargs["filling"].fuel_type == FuelType.e5.value

    def test_post_filling_data_returns_404_for_unknown_fuel_type(
        self,
        client: TestClient,
        service,
    ) -> None:
        payload = {
            "car_type": "BMW",
            "license_plate_number": "RO-AB-123",
            "timestamp": datetime.now(UTC).isoformat(),
            "mileage": 12345.6,
            "price_per_litre": 1.89,
            "litres": 42.5,
            "fuel_type": "invalid",
        }

        response = client.post("/fillings/create", json=payload)

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Fuel type 'invalid' not found"
        }

        service.save_history_record.assert_not_awaited()

    def test_delete_filling_data_returns_200(
        self,
        client: TestClient,
        service,
        user: UserRead,
    ) -> None:
        service.delete_history_record.return_value = None

        response = client.delete("/fillings/delete?filling_id=99")

        assert response.status_code == 200
        assert response.json() == {"message": "Filling deleted successfully"}

        service.delete_history_record.assert_awaited_once_with(
            history_record_id=99,
            user=user,
        )

    def test_delete_filling_data_returns_404_when_filling_not_found(
        self,
        client: TestClient,
        service,
    ) -> None:
        service.delete_history_record.side_effect = FillingNotFoundException(99)

        response = client.delete("/fillings/delete?filling_id=99")

        assert response.status_code == 404
        assert response.json() == {
            "detail": "Filling with ID 99 not found"
        }

    def test_delete_filling_data_rejects_invalid_filling_id(
        self,
        client: TestClient,
        service,
    ) -> None:
        response = client.delete("/fillings/delete?filling_id=0")

        assert response.status_code == 422
        service.delete_history_record.assert_not_awaited()