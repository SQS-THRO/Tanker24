import pytest
import pytest_asyncio
from datetime import datetime, timedelta, UTC
from unittest.mock import patch, MagicMock
from sqlalchemy import select

from app.models import TankerkoenigStation
from app.config import settings
from app.services.nearby_stations_service import NearbyStationsService
from app.dtos.gas_station_dtos import GasStation


class TestNearbyStationsServiceValidation:
	@pytest.mark.asyncio
	async def test_latitude_lower_bound(self, test_db_session):
		service = NearbyStationsService(test_db_session)

		with pytest.raises(ValueError):
			await service.get_nearby_stations(-91.0, 0.0)

	@pytest.mark.asyncio
	async def test_latitude_upper_bound(self, test_db_session):
		service = NearbyStationsService(test_db_session)

		with pytest.raises(ValueError):
			await service.get_nearby_stations(91.0, 0.0)

	@pytest.mark.asyncio
	async def test_longitude_lower_bound(self, test_db_session):
		service = NearbyStationsService(test_db_session)

		with pytest.raises(ValueError):
			await service.get_nearby_stations(0.0, -181.0)

	@pytest.mark.asyncio
	async def test_longitude_upper_bound(self, test_db_session):
		service = NearbyStationsService(test_db_session)

		with pytest.raises(ValueError):
			await service.get_nearby_stations(0.0, 181.0)

	@pytest.mark.asyncio
	async def test_valid_coordinates(self, test_db_session):
		async def mock_to_thread(func, *args, **kwargs):
			return []

		with patch("app.services.nearby_stations_service.asyncio.to_thread", new=mock_to_thread):
			service = NearbyStationsService(test_db_session)

			result = await service.get_nearby_stations(52.52, 13.405)

			assert result == []


class TestNearbyStationsServiceCache:
	@pytest.mark.asyncio
	async def test_get_nearby_stations_returns_cached_if_available(self, test_db_session):
		now = datetime.now(UTC)
		cached_station = TankerkoenigStation(
			tankerkoenig_id="cached-1",
			name="Cached Station",
			brand="Shell",
			latitude=52.52,
			longitude=13.405,
			cached_at=now,
			cache_lat=52.52,
			cache_lon=13.405,
			cache_radius=5.0,
		)
		test_db_session.add(cached_station)
		await test_db_session.commit()

		original_cache_expiry = settings.station_cache_expiry_minutes
		settings.station_cache_expiry_minutes = 60

		service = NearbyStationsService(test_db_session)

		result = await service.get_nearby_stations(52.52, 13.405)

		assert len(result) == 1
		assert result[0].name == "Cached Station"

		settings.station_cache_expiry_minutes = original_cache_expiry


class TestNearbyStationsServiceApi:
	@pytest.mark.asyncio
	async def test_get_nearby_stations_returns_empty_on_api_exception(self, test_db_session):
		with patch("app.services.nearby_stations_service.asyncio.to_thread") as mock_thread:

			async def raise_error(func, *args, **kwargs):
				raise Exception("API Error")

			mock_thread.side_effect = raise_error

			service = NearbyStationsService(test_db_session)

			result = await service.get_nearby_stations(52.0, 13.0)

			assert result == []

	@pytest.mark.asyncio
	async def test_get_nearby_stations_returns_empty_on_empty_response(self, test_db_session):
		async def mock_to_thread(func, *args, **kwargs):
			return []

		with patch("app.services.nearby_stations_service.asyncio.to_thread", new=mock_to_thread):
			service = NearbyStationsService(test_db_session)

			result = await service.get_nearby_stations(52.0, 13.0)

			assert result == []


class TestSaveStationsToCache:
	@pytest.mark.asyncio
	async def test_save_stations_to_cache_creates_new_stations(self, test_db_session):
		api_stations = [
			GasStation(
				id="station-1",
				name="Test Station 1",
				brand="Shell",
				street="Main St",
				house_number="1",
				post_code=10115,
				place="Berlin",
				latitude=52.52,
				longitude=13.405,
				distance=0.5,
				diesel=1.65,
				e5=1.75,
				e10=1.70,
				is_open=True,
			),
			GasStation(
				id="station-2",
				name="Test Station 2",
				brand="Aral",
				street="Second St",
				house_number="2",
				post_code=10117,
				place="Berlin",
				latitude=52.53,
				longitude=13.406,
				distance=1.0,
				diesel=1.66,
				e5=1.76,
				e10=1.71,
				is_open=False,
			),
		]

		service = NearbyStationsService(test_db_session)
		await service._save_stations_to_cache(api_stations, 52.52, 13.405, 5.0)

		result = await test_db_session.execute(select(TankerkoenigStation))
		stations = result.scalars().all()

		assert len(stations) == 2
		station_names = {s.name for s in stations}
		assert "Test Station 1" in station_names
		assert "Test Station 2" in station_names

	@pytest.mark.asyncio
	async def test_save_stations_to_cache_updates_existing_stations(self, test_db_session):
		now = datetime.now(UTC)
		existing_station = TankerkoenigStation(
			tankerkoenig_id="station-1",
			name="Old Name",
			brand="Shell",
			latitude=52.52,
			longitude=13.405,
			cached_at=now - timedelta(hours=1),
			cache_lat=52.52,
			cache_lon=13.405,
			cache_radius=5.0,
		)
		test_db_session.add(existing_station)
		await test_db_session.commit()

		api_stations = [
			GasStation(
				id="station-1",
				name="Updated Name",
				brand="Shell",
				street="Main St",
				house_number="1",
				post_code=10115,
				place="Berlin",
				latitude=52.52,
				longitude=13.405,
				distance=0.5,
				diesel=1.65,
				e5=1.75,
				e10=1.70,
				is_open=True,
			),
		]

		service = NearbyStationsService(test_db_session)
		await service._save_stations_to_cache(api_stations, 52.52, 13.405, 5.0)

		result = await test_db_session.execute(select(TankerkoenigStation))
		stations = result.scalars().all()

		assert len(stations) == 1
		assert stations[0].name == "Updated Name"
