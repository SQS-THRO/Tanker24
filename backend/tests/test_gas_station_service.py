import pytest
import httpx
import respx
from app.services.gas_station_service import TankerkoenigGasStationService, GasStationService
from datetime import datetime


class TestGasStationService:
	# Smoke test
	def test_get_stations(self):
		service = TankerkoenigGasStationService()
		assert isinstance(service, GasStationService)

		result = service.get_gas_stations(latitude=52.521, longitude=13.438, radius=5)
		assert isinstance(result, list)

	# Test api_key assignment through interface
	def test_tankerkoenig_service_stores_api_key(self):
		service = TankerkoenigGasStationService(api_key="test-key")
		assert service.api_key == "test-key"

	# Helper test fixture to reduce duplicate code
	@pytest.fixture
	def station_response_factory(self):
		def _factory(**override_parameters):
			data = {
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
			}
			data["station"].update(override_parameters)
			return data

		return _factory

	@respx.mock
	def test_get_gas_station_by_id_with_respx(self, station_response_factory):
		route = respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(
				200,
				json=station_response_factory(),
			)
		)

		service = TankerkoenigGasStationService(api_key="test-api-key")
		result = service.get_gas_station_by_id("123")

		assert route.called
		assert result.id == "123"
		assert result.name == "Test Station"

	@respx.mock
	def test_get_gas_station_by_id_success(self, station_response_factory):
		respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(
				200,
				json=station_response_factory(
					openingTimes=[
						{
							"text": "Mon-Fri",
							"start": "08:00:00",
							"end": "20:00:00",
						}
					]
				),
			)
		)

		service = TankerkoenigGasStationService(api_key="test-api-key")
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
		assert pytest.approx(result.distance) == pytest.approx(1.2)
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

	# Test with empty opening times
	@respx.mock
	def test_get_gas_station_by_id_empty_opening_times(self, station_response_factory):
		respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(
				200,
				json=station_response_factory(),
			)
		)

		service = TankerkoenigGasStationService()
		result = service.get_gas_station_by_id("123")

		assert result.opening_times == []

	# Check if the Runtime errors are thrown
	@respx.mock
	def test_get_gas_station_by_id_api_error(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(
				200,
				json={"ok": False},
			)
		)

		service = TankerkoenigGasStationService()

		with pytest.raises(
			RuntimeError,
			match="unable to return the data for a specific station",
		):
			service.get_gas_station_by_id("123")

	@respx.mock
	def test_get_gas_station_by_id_http_error(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(500, json={}),
		)

		service = TankerkoenigGasStationService()

		with pytest.raises(httpx.HTTPStatusError):
			service.get_gas_station_by_id("123")

	# Check if all params are mapped through
	@respx.mock
	def test_get_gas_station_by_id_sends_correct_params(self, station_response_factory):
		route = respx.get("https://creativecommons.tankerkoenig.de/json/detail.php").mock(
			return_value=httpx.Response(
				200,
				json=station_response_factory(),
			)
		)

		service = TankerkoenigGasStationService(api_key="test-api-key")
		service.get_gas_station_by_id("123")

		assert route.called
		request = route.calls[0].request
		assert request.url.params["id"] == "123"
		assert request.url.params["apikey"] == "test-api-key"

	# Check the handling of a response with multiple stations
	@respx.mock
	def test_get_gas_stations_success(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/list.php").mock(
			return_value=httpx.Response(
				200,
				json={
					"ok": True,
					"stations": [
						{
							"id": "1",
							"name": "Station A",
							"brand": "Shell",
							"street": "Street A",
							"houseNumber": "10",
							"postCode": 10115,
							"place": "Berlin",
							"lat": 52.52,
							"lng": 13.405,
							"dist": 0.4,
							"isOpen": True,
							"diesel": 1.65,
							"e5": 1.75,
							"e10": 1.70,
						},
						{
							"id": "2",
							"name": "Station B",
							"brand": "Aral",
							"street": "Street B",
							"houseNumber": "20",
							"postCode": 10117,
							"place": "Berlin",
							"lat": 52.521,
							"lng": 13.406,
							"dist": 0.8,
							"isOpen": False,
							"diesel": 1.66,
							"e5": 1.76,
							"e10": 1.71,
						},
					],
				},
			)
		)

		service = TankerkoenigGasStationService(api_key="test-api-key")
		result = service.get_gas_stations(52.52, 13.405, 5.0)

		assert len(result) == 2

		assert result[0].id == "1"
		assert result[0].name == "Station A"
		assert result[0].brand == "Shell"
		assert result[0].street == "Street A"
		assert result[0].house_number == "10"
		assert result[0].post_code == 10115
		assert result[0].place == "Berlin"
		assert pytest.approx(result[0].latitude) == pytest.approx(52.52)
		assert pytest.approx(result[0].longitude) == pytest.approx(13.405)
		assert pytest.approx(result[0].distance) == pytest.approx(0.4)
		assert result[0].is_open is True
		assert pytest.approx(result[0].diesel) == pytest.approx(1.65)
		assert pytest.approx(result[0].e5) == pytest.approx(1.75)
		assert pytest.approx(result[0].e10) == pytest.approx(1.70)

		assert result[1].id == "2"
		assert result[1].name == "Station B"
		assert result[1].is_open is False

	# Check the handling of an empty stations response
	@respx.mock
	def test_get_gas_stations_empty_list(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/list.php").mock(
			return_value=httpx.Response(
				200,
				json={
					"ok": True,
					"stations": [],
				},
			)
		)

		service = TankerkoenigGasStationService()
		result = service.get_gas_stations(52.52, 13.405, 5.0)

		assert result == []

	# Check if the api errors are thrown correctly
	@respx.mock
	def test_get_gas_stations_api_error(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/list.php").mock(
			return_value=httpx.Response(
				200,
				json={"ok": False},
			)
		)

		service = TankerkoenigGasStationService()

		with pytest.raises(RuntimeError, match="Tankerkoenig API returned an error"):
			service.get_gas_stations(52.52, 13.405, 5.0)

	# Test how the service reacts if the endpoint sends an internal server error status code.
	# This is a valid test because the api is provided based on best-effort.
	@respx.mock
	def test_get_gas_stations_http_error(self):
		respx.get("https://creativecommons.tankerkoenig.de/json/list.php").mock(
			return_value=httpx.Response(500, json={}),
		)

		service = TankerkoenigGasStationService()

		with pytest.raises(httpx.HTTPStatusError):
			service.get_gas_stations(52.52, 13.405, 5.0)

	# Check if the params are mapped correctly to the url query
	@respx.mock
	def test_get_gas_stations_sends_correct_params(self):
		route = respx.get("https://creativecommons.tankerkoenig.de/json/list.php").mock(
			return_value=httpx.Response(
				200,
				json={
					"ok": True,
					"stations": [],
				},
			)
		)

		service = TankerkoenigGasStationService(api_key="test-api-key")
		service.get_gas_stations(52.52, 13.405, 5.0)

		assert route.called
		request = route.calls[0].request
		assert request.url.params["lat"] == "52.52"
		assert request.url.params["lng"] == "13.405"
		assert request.url.params["rad"] == "5.0"
		assert request.url.params["sort"] == "dist"
		assert request.url.params["type"] == "all"
		assert request.url.params["apikey"] == "test-api-key"
