import time
from datetime import datetime, UTC, timedelta

import pytest

from app.models import Station, Car, FuelType, HistoryRecord
from app.repositories.station_repository import StationRepository
from app.services.fillings_service import FillingsService
from app.services.export_data_service import NestedExportDataService, FlatExportDataService
from app.dtos.gas_station_dtos import GasStation


pytestmark = pytest.mark.asyncio


class TestStationQueryPerformance:
	STATION_COUNT = 500

	async def _bulk_insert_stations(self, db_session, count: int) -> None:
		now = datetime.now(UTC).replace(tzinfo=None)
		stations = [
			Station(
				tankerkoenig_id=f"perf-uuid-{i:04d}",
				name=f"Station {i}",
				brand="Shell" if i % 2 == 0 else "Aral",
				street=f"Street {i}",
				house_number=str(i),
				post_code=10115 + (i % 100),
				place="Berlin",
				latitude=52.50 + (i * 0.001),
				longitude=13.40 + (i * 0.001),
				distance=i * 0.1,
				diesel=1.65 + (i * 0.001),
				e5=1.75 + (i * 0.001),
				e10=1.70 + (i * 0.001),
				is_open=True,
				cached_at=now,
				cache_lat=52.52,
				cache_lon=13.405,
				cache_radius=5.0,
			)
			for i in range(count)
		]
		for s in stations:
			db_session.add(s)
		await db_session.commit()

	async def test_get_all_stations_scalability(self, test_db_session):
		await self._bulk_insert_stations(test_db_session, self.STATION_COUNT)
		repo = StationRepository(test_db_session)

		start = time.perf_counter()
		result = await repo.get_all_stations()
		duration = time.perf_counter() - start

		assert len(result) == self.STATION_COUNT, "All stations should be returned"
		assert duration < 2.0, (
			f"get_all_stations with {self.STATION_COUNT} rows should complete in < 2s (took {duration:.3f}s)"
		)

	async def test_get_cached_stations_scalability(self, test_db_session):
		await self._bulk_insert_stations(test_db_session, self.STATION_COUNT)
		repo = StationRepository(test_db_session)
		min_time = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1)

		start = time.perf_counter()
		result = await repo.get_cached_stations(52.52, 13.405, 5.0, min_time, 0.5)
		duration = time.perf_counter() - start

		assert len(result) == self.STATION_COUNT
		assert duration < 2.0, (
			f"get_cached_stations with {self.STATION_COUNT} rows should complete in < 2s (took {duration:.3f}s)"
		)

	async def test_upsert_stations_performance(self, test_db_session):
		api_stations = [
			GasStation(
				id=f"perf-upsert-{i:04d}",
				name=f"Station {i}",
				brand="Shell",
				street="Main St",
				house_number=str(i),
				post_code=10115,
				place="Berlin",
				latitude=52.52,
				longitude=13.405,
				distance=i * 0.1,
				diesel=1.65,
				e5=1.75,
				e10=1.70,
				is_open=True,
			)
			for i in range(200)
		]
		repo = StationRepository(test_db_session)

		start = time.perf_counter()
		await repo.upsert_stations(api_stations, 52.52, 13.405, 5.0)
		duration = time.perf_counter() - start

		assert duration < 5.0, f"upsert_stations with 200 rows should complete in < 5s (took {duration:.3f}s)"

		all_stations = await repo.get_all_stations()
		assert len(all_stations) == 200


class TestFillingsQueryPerformance:
	CAR_COUNT = 10
	RECORDS_PER_CAR = 100
	TOTAL_RECORDS = CAR_COUNT * RECORDS_PER_CAR

	async def _bulk_insert_fillings(self, test_db_session, test_user, fuel_type) -> None:
		cars = [
			Car(
				type="Limousine",
				license_plate_number=f"RO-AB-{i:03d}",
				owner_id=test_user.id,
			)
			for i in range(self.CAR_COUNT)
		]
		for c in cars:
			test_db_session.add(c)
		await test_db_session.commit()
		for c in cars:
			await test_db_session.refresh(c)

		records = [
			HistoryRecord(
				timestamp=datetime.now(UTC),
				mileage=1000.0 + (i * 100) + (j * 10),
				price_per_litre=1.80 + (j * 0.01),
				litres=40.0 + (j * 0.5),
				car_id=cars[i].id,
				fuel_type_id=fuel_type.id,
				tankerkoenig_station_id=f"station-{i}-{j}",
			)
			for i in range(self.CAR_COUNT)
			for j in range(self.RECORDS_PER_CAR)
		]
		for r in records:
			test_db_session.add(r)
		await test_db_session.commit()

	async def test_get_filling_dto_for_user_scalability(self, test_db_session, test_user):
		fuel_type = FuelType(name="e5")
		test_db_session.add(fuel_type)
		await test_db_session.commit()
		await test_db_session.refresh(fuel_type)

		await self._bulk_insert_fillings(test_db_session, test_user, fuel_type)
		service = FillingsService(test_db_session)

		start = time.perf_counter()
		result = await service.get_filling_dto_for_user(test_user)
		duration = time.perf_counter() - start

		assert len(result) == self.TOTAL_RECORDS
		assert duration < 5.0, (
			f"get_filling_dto_for_user with {self.CAR_COUNT} cars and "
			f"{self.RECORDS_PER_CAR} records each should complete in < 5s "
			f"(took {duration:.3f}s)"
		)

	async def test_nested_export_scalability(self, test_db_session, test_user):
		fuel_type = FuelType(name="e5")
		test_db_session.add(fuel_type)
		await test_db_session.commit()
		await test_db_session.refresh(fuel_type)

		await self._bulk_insert_fillings(test_db_session, test_user, fuel_type)
		service = NestedExportDataService(test_db_session)

		start = time.perf_counter()
		result = await service.get_user_data(test_user.id)
		duration = time.perf_counter() - start

		assert len(result) == self.CAR_COUNT
		total_records = sum(len(car["history"]) for car in result)
		assert total_records == self.TOTAL_RECORDS
		assert duration < 5.0, (
			f"NestedExportDataService with {self.CAR_COUNT} cars and "
			f"{self.RECORDS_PER_CAR} records each should complete in < 5s "
			f"(took {duration:.3f}s)"
		)

	async def test_flat_export_scalability(self, test_db_session, test_user):
		fuel_type = FuelType(name="e5")
		test_db_session.add(fuel_type)
		await test_db_session.commit()
		await test_db_session.refresh(fuel_type)

		await self._bulk_insert_fillings(test_db_session, test_user, fuel_type)
		service = FlatExportDataService(test_db_session)

		start = time.perf_counter()
		result = await service.get_user_data(test_user.id)
		duration = time.perf_counter() - start

		assert len(result) == self.TOTAL_RECORDS
		assert duration < 5.0, (
			f"FlatExportDataService with {self.CAR_COUNT} cars and "
			f"{self.RECORDS_PER_CAR} records each should complete in < 5s "
			f"(took {duration:.3f}s)"
		)


class TestApiEndpointPerformance:
	STATION_COUNT = 300

	async def _seed_stations(self, test_db_session) -> None:
		now = datetime.now(UTC).replace(tzinfo=None)
		stations = [
			Station(
				tankerkoenig_id=f"api-perf-{i:04d}",
				name=f"Station {i}",
				brand="Shell",
				latitude=52.50 + (i * 0.001),
				longitude=13.40 + (i * 0.001),
				distance=i * 0.1,
				diesel=1.65,
				e5=1.75,
				e10=1.70,
				is_open=True,
				cached_at=now,
				cache_lat=52.52,
				cache_lon=13.405,
				cache_radius=5.0,
			)
			for i in range(self.STATION_COUNT)
		]
		for s in stations:
			test_db_session.add(s)
		await test_db_session.commit()

	async def test_list_stations_response_time(self, authenticated_client, test_db_session):
		await self._seed_stations(test_db_session)

		start = time.perf_counter()
		response = await authenticated_client.get("/api/v0/stations/")
		duration = time.perf_counter() - start

		assert response.status_code == 200
		data = response.json()
		assert len(data) == self.STATION_COUNT
		assert duration < 3.0, (
			f"GET /api/v0/stations/ with {self.STATION_COUNT} stations should respond in < 3s (took {duration:.3f}s)"
		)


class TestNearbyStationsCachePerformance:
	STATION_COUNT = 1000

	async def _seed_cached_stations(self, test_db_session, latitude, longitude, radius) -> None:
		now = datetime.now(UTC).replace(tzinfo=None)
		stations = [
			Station(
				tankerkoenig_id=f"cache-perf-{i:04d}",
				name=f"Cached Station {i}",
				brand="Shell",
				latitude=latitude + (i * 0.0005),
				longitude=longitude + (i * 0.0005),
				distance=i * 0.05,
				diesel=1.65,
				e5=1.75,
				e10=1.70,
				is_open=True,
				cached_at=now,
				cache_lat=latitude,
				cache_lon=longitude,
				cache_radius=radius,
			)
			for i in range(self.STATION_COUNT)
		]
		for s in stations:
			test_db_session.add(s)
		await test_db_session.commit()

	async def test_nearby_stations_cache_hit_with_many_records(self, test_db_session):
		lat, lon, radius = 52.52, 13.405, 5.0
		await self._seed_cached_stations(test_db_session, lat, lon, radius)

		repo = StationRepository(test_db_session)
		min_time = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=1)

		start = time.perf_counter()
		result = await repo.get_cached_stations(lat, lon, radius, min_time, 0.5)
		duration = time.perf_counter() - start

		assert len(result) == self.STATION_COUNT
		assert duration < 2.0, (
			f"get_cached_stations with {self.STATION_COUNT} cached stations "
			f"should complete in < 2s (took {duration:.3f}s)"
		)
