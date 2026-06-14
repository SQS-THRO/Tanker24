import pytest


@pytest.mark.asyncio
class TestStationList:
	async def test_list_stations_authenticated_empty(self, authenticated_client):
		response = await authenticated_client.get("/api/v0/stations/")

		assert response.status_code == 200
		assert response.json() == []

	async def test_list_stations_authenticated_with_stations(self, authenticated_client, cached_station):
		response = await authenticated_client.get("/api/v0/stations/")

		assert response.status_code == 200
		data = response.json()
		assert len(data) == 1
		assert data[0]["name"] == cached_station.name
		assert data[0]["tankerkoenig_id"] == cached_station.tankerkoenig_id
		assert data[0]["brand"] == cached_station.brand

	async def test_list_stations_unauthenticated(self, async_client):
		response = await async_client.get("/api/v0/stations/")

		assert response.status_code == 401

	async def test_list_stations_multiple_stations(self, authenticated_client, test_db_session):
		from app.models import Station
		from datetime import datetime, UTC

		now = datetime.now(UTC).replace(tzinfo=None)
		stations = [
			Station(
				tankerkoenig_id=f"uuid-{i}",
				name=f"Station {i}",
				brand="Shell",
				street="Baumstraße",
				house_number="1",
				post_code="83026",
				place="Rosenheim",
				latitude=52.0 + i * 0.1,
				longitude=13.0 + i * 0.1,
				cached_at=now,
			)
			for i in range(3)
		]
		for s in stations:
			test_db_session.add(s)
		await test_db_session.commit()

		response = await authenticated_client.get("/api/v0/stations/")

		assert response.status_code == 200
		data = response.json()
		assert len(data) == 3


@pytest.mark.asyncio
class TestStationListUnauthenticated:
	async def test_list_stations_returns_401_without_auth(self, async_client):
		response = await async_client.get("/api/v0/stations/")

		assert response.status_code == 401


@pytest.mark.asyncio
class TestGetNearbyStations:
	@pytest.fixture(autouse=True)
	def clear_rate_limiter(self):
		from app.limiter import limiter

		limiter._storage.storage.clear()
		limiter._storage.expirations.clear()
		yield
		limiter._storage.storage.clear()
		limiter._storage.expirations.clear()

	async def test_nearby_stations_value_error_returns_400(self, authenticated_client):
		from unittest.mock import patch, AsyncMock

		with patch("app.routers.stations.NearbyStationsService") as mock_service_class:
			mock_instance = mock_service_class.return_value
			mock_instance.get_nearby_stations = AsyncMock(side_effect=ValueError("Invalid coordinates"))

			response = await authenticated_client.get("/api/v0/stations/nearby?latitude=52.52&longitude=13.405")

		assert response.status_code == 400
		assert response.json()["detail"] == "Invalid coordinates"
