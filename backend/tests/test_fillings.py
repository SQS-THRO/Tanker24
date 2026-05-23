# tests/routers/test_fillings.py
import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.auth import get_current_active_user
from app.dependencies import get_fillings_service
from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.exceptions.exceptions import FillingNotFoundException
from app.routers.fillings import router, post_filling_data, delete_filling_data, get_filling_data_from_user
from app.schemas.user import UserRead
from app.services.fillings_service import FillingsService


class TestFillingsConnectivity:
    TEST_PASSWORD = "test-password" #NO SONAR
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
    def service(self):
        service = AsyncMock()
        service.save_history_record = AsyncMock()
        service.delete_history_record = AsyncMock()
        return service

    @pytest.fixture
    def client(self, user, service) -> TestClient:
        app = FastAPI()
        app.include_router(router)

        def override_current_user():
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
            "license_plate_number": "RO-AB-123",
            "car_type": "Schräghecklimousine",
            "mileage": 666,
            "timestamp": "2026-05-23T10:25:31.482193+00:00",
            "price_per_litre": 2.03,
            "litres": 17.6,
            "tankerkoenig_station_id": "213215465123153465123135131",
            "fuel_type": "e5"
        }

        response = client.post("/fillings/create", json=payload)

        assert response.status_code == 200
        assert response.json() == {"message": "Filling stored successfully"}

        service.save_history_record.assert_awaited_once()
        _, kwargs = service.save_history_record.call_args

        assert kwargs["user"] == user
        assert kwargs["filling"].license_plate_number == "RO-AB-123"
        assert kwargs["filling"].fuel_type == FuelType.e5.value

    def test_post_filling_data_returns_422_for_unknown_fuel_type(
        self,
        client: TestClient,
        service,
    ) -> None:
        payload = {
            "car_type": "Limousine",
            "license_plate_number": "RO-AB-123",
            "timestamp":  "2026-05-23T10:25:31.482193+00:00",
            "mileage": 12345.6,
            "price_per_litre": 1.89,
            "litres": 42.5,
            "tankerkoenig_station_id": "213215465123153465123135131",
            "fuel_type": "invalid",
        }

        response = client.post("/fillings/create", json=payload)

        assert response.status_code == 422
        assert response.json()["detail"][0]["loc"] == ["body", "fuel_type"]

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


class TestFillingsFunctionality:
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

    @pytest.fixture()
    def filling_dto(self) -> FillingDTO:
        return FillingDTO(
            car_type="Limousine",
            license_plate_number="RO-AB-123",
            timestamp="2026-05-23T10:25:31.482193+00:00",
            mileage=12345.6,
            price_per_litre= 1.89,
            litres= 42.5,
            tankerkoenig_station_id="213215465123153465123135131",
            fuel_type="e5",
        )

    @pytest.fixture
    def service(self) -> Mock(spec=FillingsService):
        service = Mock(spec=FillingsService)
        service.save_history_record = AsyncMock()
        service.delete_history_record = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_post_filling_data_successfully(self, user,
                                                  filling_dto: FillingDTO,
                                                service: FillingsService) -> None:
        response = await post_filling_data(
            filling=filling_dto,
            service=service,
            user=user,
        )

        assert response.status_code == 200
        assert response.body == b'{"message":"Filling stored successfully"}'

        service.save_history_record.assert_awaited_once_with(
            filling=filling_dto,
            user=user,
        )

        assert filling_dto.license_plate_number == "RO-AB-123"

    @pytest.mark.asyncio
    async def test_post_filling_data_unsuccessfully(self, user,
                                                  filling_dto: FillingDTO,
                                                  service: FillingsService) -> None:
        filling_dto.fuel_type = "invalid"
        try:
            await post_filling_data(
                filling=filling_dto,
                service=service,
                user=user,
            )
        except Exception as e:
            assert isinstance(e, HTTPException)
            assert e.status_code == 404
            assert e.detail == "Fuel type \'invalid\' not found"

    @pytest.mark.asyncio
    async def test_delete_filling_data_unsuccessfully(self, user,
                                                    service: FillingsService) -> None:
        service.delete_history_record.side_effect = FillingNotFoundException(91)
        try:
            await delete_filling_data(filling_id=91, user=user,service=service)
        except Exception as e:
            assert isinstance(e, HTTPException)
            assert e.status_code == 404

        service.delete_history_record.assert_awaited_once_with(
            history_record_id=91,
            user=user,
        )

    @pytest.mark.asyncio
    async def test_delete_filling_data_successfully(
            self,
            user: UserRead,
            service: FillingsService,
    ) -> None:
        response = await delete_filling_data(
            filling_id=1,
            user=user,
            service=service,
        )

        assert response.status_code == 200
        assert response.body == b'{"message":"Filling deleted successfully"}'

        service.delete_history_record.assert_awaited_once_with(
            history_record_id=1,
            user=user,
        )

    @pytest.mark.asyncio
    async def test_get_filling_data_from_user_successfully(
            self,
            user: UserRead,
            service: FillingsService,
    ) -> None:
        payload = [
            {
                "id": 1,
                "mileage": 12345.6,
                "price_per_litre": 1.89,
                "litres": 42.5,
                "car_id": 10,
                "fuel_type_id": 2,
                "timestamp": "2026-05-23T10:25:31.482193+00:00",
                "tankerkoenig_station_id": "ABC123456789"
            }
        ]
        service.get_history_records_for_user.return_value = payload

        response = await get_filling_data_from_user(
            user=user,
            service=service,
        )

        assert isinstance(response, JSONResponse)
        assert response.status_code == 200

        service.get_history_records_for_user.assert_awaited_once_with(
            user=user,
        )

        assert json.loads(response.body) == payload

    @pytest.mark.asyncio
    async def test_get_filling_data_from_user_returns_empty_list(
            self,
            user: UserRead,
            service: FillingsService,
    ) -> None:
        service.get_history_records_for_user.return_value = []

        response = await get_filling_data_from_user(
            user=user,
            service=service,
        )

        assert response.status_code == 200
        assert response.body == b"[]"

        service.get_history_records_for_user.assert_awaited_once_with(
            user=user,
        )
