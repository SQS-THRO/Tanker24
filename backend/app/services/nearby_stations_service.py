from datetime import datetime, timedelta, UTC
import asyncio

from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dtos.gas_station_dtos import GasStation
from app.models import TankerkoenigStation
from app.schemas.station import TankerkoenigStation as TankerkoenigStationSchema
from app.services.gas_station_service import TankerkoenigGasStationService
from app.services.rate_limiter import global_rate_limiter


class NearbyStationsService:
	def __init__(self, db: AsyncSession):
		self.db = db
		self.gas_station_service = TankerkoenigGasStationService(api_key=settings.tankerkoenig_api_key)

	async def get_nearby_stations(self, latitude: float, longitude: float) -> list[TankerkoenigStationSchema]:
		if not (-90 <= latitude <= 90):
			raise ValueError("Latitude must be between -90 and 90")
		if not (-180 <= longitude <= 180):
			raise ValueError("Longitude must be between -180 and 180")

		radius = settings.tankerkoenig_search_radius_km
		cache_expiry = timedelta(minutes=settings.station_cache_expiry_minutes)
		now = datetime.now(UTC)

		cached_stations = await self._get_cached_stations(latitude, longitude, radius, now - cache_expiry)

		if cached_stations is not None:
			return cached_stations

		await global_rate_limiter.wait_for_token()

		try:
			api_stations = await asyncio.to_thread(
				self.gas_station_service.get_gas_stations, latitude=latitude, longitude=longitude, radius=radius
			)
		except Exception:
			return []

		if not api_stations:
			return []

		await self._save_stations_to_cache(api_stations, latitude, longitude, radius)

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
		result = await self.db.execute(
			select(TankerkoenigStation)
			.where(
				and_(
					TankerkoenigStation.cache_lat.isnot(None),
					TankerkoenigStation.cache_lon.isnot(None),
					TankerkoenigStation.cache_radius == radius,
					TankerkoenigStation.cached_at >= min_cached_at,
					TankerkoenigStation.cache_lat.between(latitude - tolerance, latitude + tolerance),
					TankerkoenigStation.cache_lon.between(longitude - tolerance, longitude + tolerance),
				)
			)
			.order_by(TankerkoenigStation.distance)
		)
		stations = result.scalars().all()
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
		now = datetime.now(UTC)

		result = await self.db.execute(
			select(TankerkoenigStation.tankerkoenig_id).where(
				and_(
					TankerkoenigStation.cache_lat.isnot(None),
					TankerkoenigStation.cache_lon.isnot(None),
					TankerkoenigStation.cache_radius == cache_radius,
				)
			)
		)
		existing_ids = {row[0] for row in result.fetchall()}

		new_ids = {s.id for s in api_stations}

		ids_to_delete = existing_ids - new_ids
		if ids_to_delete:
			await self.db.execute(
				delete(TankerkoenigStation).where(TankerkoenigStation.tankerkoenig_id.in_(ids_to_delete))
			)

		for station in api_stations:
			existing_record = await self.db.execute(
				select(TankerkoenigStation).where(TankerkoenigStation.tankerkoenig_id == station.id)
			)
			db_station = existing_record.scalar_one_or_none()

			if db_station:
				db_station.name = station.name
				db_station.brand = station.brand
				db_station.street = station.street
				db_station.house_number = station.house_number
				db_station.post_code = station.post_code
				db_station.place = station.place
				db_station.latitude = station.latitude
				db_station.longitude = station.longitude
				db_station.distance = station.distance
				db_station.diesel = station.diesel
				db_station.e5 = station.e5
				db_station.e10 = station.e10
				db_station.is_open = station.is_open
				db_station.cached_at = now
				db_station.cache_lat = cache_lat
				db_station.cache_lon = cache_lon
				db_station.cache_radius = cache_radius
			else:
				db_station = TankerkoenigStation(
					tankerkoenig_id=station.id,
					name=station.name,
					brand=station.brand,
					street=station.street,
					house_number=station.house_number,
					post_code=station.post_code,
					place=station.place,
					latitude=station.latitude,
					longitude=station.longitude,
					distance=station.distance,
					diesel=station.diesel,
					e5=station.e5,
					e10=station.e10,
					is_open=station.is_open,
					cached_at=now,
					cache_lat=cache_lat,
					cache_lon=cache_lon,
					cache_radius=cache_radius,
				)
				self.db.add(db_station)

		await self.db.commit()
