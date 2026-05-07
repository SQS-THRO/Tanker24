import logging
from datetime import datetime, timedelta, UTC
import asyncio

from app.config import settings
from app.dtos.gas_station_dtos import GasStation
from app.schemas.station import TankerkoenigStation as TankerkoenigStationSchema
from app.repositories.tankerkoenig_station_repository import TankerkoenigStationRepository
from app.services.gas_station_service import TankerkoenigGasStationService
from app.services.rate_limiter import global_rate_limiter

logger = logging.getLogger("app.nearby_stations_service")


class NearbyStationsService:
	def __init__(self, repository: TankerkoenigStationRepository):
		self.repository = repository
		self.gas_station_service = TankerkoenigGasStationService(api_key=settings.tankerkoenig_api_key)

	async def get_nearby_stations(self, latitude: float, longitude: float) -> list[TankerkoenigStationSchema]:
		if not (-90 <= latitude <= 90):
			raise ValueError("Latitude must be between -90 and 90")
		if not (-180 <= longitude <= 180):
			raise ValueError("Longitude must be between -180 and 180")

		radius = settings.tankerkoenig_search_radius_km
		cache_expiry = timedelta(minutes=settings.station_cache_expiry_minutes)
		now = datetime.now(UTC).replace(tzinfo=None)

		cached_stations = await self._get_cached_stations(latitude, longitude, radius, now - cache_expiry)

		if cached_stations is not None:
			logger.debug(
				"Cache hit for nearby stations: lat=%.4f lon=%.4f (%d results)",
				latitude,
				longitude,
				len(cached_stations),
			)
			return cached_stations

		logger.info("Cache miss for nearby stations: lat=%.4f lon=%.4f, fetching from API", latitude, longitude)

		await global_rate_limiter.wait_for_token()

		try:
			api_stations = await asyncio.to_thread(
				self.gas_station_service.get_gas_stations, latitude=latitude, longitude=longitude, radius=radius
			)
		except Exception:
			logger.exception("Failed to fetch stations from Tankerkoenig API: lat=%.4f lon=%.4f", latitude, longitude)
			return []

		if not api_stations:
			logger.info("No stations found from API: lat=%.4f lon=%.4f", latitude, longitude)
			return []

		logger.info("Fetched %d stations from API: lat=%.4f lon=%.4f", len(api_stations), latitude, longitude)

		await self.repository.upsert_stations(api_stations, latitude, longitude, radius)

		result = await self._get_cached_stations(latitude, longitude, radius, datetime.min)
		return result if result is not None else []

	async def _get_cached_stations(
		self,
		latitude: float,
		longitude: float,
		radius: float,
		min_cached_at: datetime,
	) -> list[TankerkoenigStationSchema] | None:
		tolerance = settings.station_cache_tolerance_km
		stations = await self.repository.get_cached_stations(latitude, longitude, radius, min_cached_at, tolerance)
		if stations:
			return [TankerkoenigStationSchema.model_validate(s) for s in stations]
		return None

	async def _save_stations_to_cache(
		self,
		api_stations: list[GasStation],
		cache_lat: float,
		cache_lon: float,
		cache_radius: float,
	) -> None:
		await self.repository.upsert_stations(api_stations, cache_lat, cache_lon, cache_radius)
