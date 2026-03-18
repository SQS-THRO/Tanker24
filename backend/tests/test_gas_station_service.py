import pytest
import httpx
import respx
from app.services.gas_station_service import GasStationService
from datetime import datetime
from app.dtos.gas_station_dtos import GasStation, OpeningTime, FuelType

class TestGasStationService:
    def test_get_stations(self):
        service = GasStationService()
        result = service.get_gas_stations(latitude=52.521, longitude=13.438, radius=5)

        assert isinstance(result, list)

    @respx.mock
    def test_get_gas_station_by_id_with_respx(self):
        route = respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
            return_value=httpx.Response(
                200,
                json={
                    "ok": True,
                    "station": {
                        "id": "123",
                        "name": "Test Station",
                        "brand": "Aral",
                        "street": "Main Street",
                        "houseNumber": "1",
                        "postCode": 80331,
                        "place": "Munich",
                        "lat": 48.137,
                        "lng": 11.575,
                        "dist": 1.2,
                        "isOpen": True,
                        "diesel": 1.689,
                        "e5": 1.789,
                        "e10": 1.729,
                        "wholeDay": False,
                        "overrides": False,
                        "openingTimes": [],
                    },
                },
            )
        )

        service = GasStationService(api_key="test-api-key")
        result = service.get_gas_station_by_id("123")

        assert route.called
        assert result.id == "123"
        assert result.name == "Test Station"

    @respx.mock
    def test_get_gas_station_by_id_success(self):
        respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
            return_value=httpx.Response(
                200,
                json={
                    "ok": True,
                    "station": {
                        "id": "123",
                        "name": "Test Station",
                        "brand": "Aral",
                        "street": "Main Street",
                        "houseNumber": "1",
                        "postCode": 80331,
                        "place": "Munich",
                        "lat": 48.137,
                        "lng": 11.575,
                        "dist": 1.2,
                        "isOpen": True,
                        "diesel": 1.689,
                        "e5": 1.789,
                        "e10": 1.729,
                        "wholeDay": False,
                        "overrides": False,
                        "openingTimes": [
                            {
                                "text": "Mon-Fri",
                                "start": "08:00:00",
                                "end": "20:00:00",
                            }
                        ],
                    },
                },
            )
        )

        service = GasStationService(api_key="test-api-key")
        result = service.get_gas_station_by_id("123")

        assert result.id == "123"
        assert result.name == "Test Station"
        assert result.brand == "Aral"
        assert result.street == "Main Street"
        assert result.house_number == "1"
        assert result.post_code == 80331
        assert result.place == "Munich"
        assert pytest.approx(result.latitude) == pytest.approx(48.137)
        assert pytest.approx(result.longitude) == pytest.approx(11.575)
        assert pytest.approx(result.distance) ==  pytest.approx(1.2)
        assert result.is_open is True
        assert pytest.approx(result.diesel) == pytest.approx(1.689)
        assert pytest.approx(result.e5) == pytest.approx(1.789)
        assert pytest.approx(result.e10) == pytest.approx(1.729)
        assert result.whole_day is False
        assert result.overrides is False

        assert len(result.opening_times) == 1
        assert result.opening_times[0].text == "Mon-Fri"
        assert result.opening_times[0].start == datetime.strptime("08:00:00", "%H:%M:%S").time()
        assert result.opening_times[0].end == datetime.strptime("20:00:00", "%H:%M:%S").time()