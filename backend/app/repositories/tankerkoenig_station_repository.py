from datetime import datetime, UTC

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.gas_station_dtos import GasStation
from app.models import TankerkoenigStation


class TankerkoenigStationRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_cached_stations(
		self,
		latitude: float,
		longitude: float,
		radius: float,
		min_cached_at: datetime,
		tolerance: float,
	) -> list[TankerkoenigStation]:
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
		return list(result.scalars().all())

	async def get_existing_cached_ids(self, cache_radius: float) -> set[str]:
		result = await self.db.execute(
			select(TankerkoenigStation.tankerkoenig_id).where(
				and_(
					TankerkoenigStation.cache_lat.isnot(None),
					TankerkoenigStation.cache_lon.isnot(None),
					TankerkoenigStation.cache_radius == cache_radius,
				)
			)
		)
		return {row[0] for row in result.fetchall()}

	async def delete_by_tankerkoenig_ids(self, ids: set[str]) -> None:
		if ids:
			await self.db.execute(delete(TankerkoenigStation).where(TankerkoenigStation.tankerkoenig_id.in_(ids)))

	async def find_by_tankerkoenig_id(self, tankerkoenig_id: str) -> TankerkoenigStation | None:
		result = await self.db.execute(
			select(TankerkoenigStation).where(TankerkoenigStation.tankerkoenig_id == tankerkoenig_id)
		)
		return result.scalar_one_or_none()

	async def upsert_stations(
		self,
		api_stations: list[GasStation],
		cache_lat: float,
		cache_lon: float,
		cache_radius: float,
	) -> None:
		now = datetime.now(UTC).replace(tzinfo=None)

		existing_ids = await self.get_existing_cached_ids(cache_radius)
		new_ids = {s.id for s in api_stations}

		ids_to_delete = existing_ids - new_ids
		await self.delete_by_tankerkoenig_ids(ids_to_delete)

		for station in api_stations:
			db_station = await self.find_by_tankerkoenig_id(station.id)

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
