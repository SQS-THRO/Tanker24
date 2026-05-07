from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Station
from app.schemas.station import StationCreate, StationUpdate


class StationRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_stations_by_owner(self, owner_id: int) -> List[Station]:
		result = await self.db.execute(select(Station).where(Station.owner_id == owner_id))
		return list(result.scalars().all())

	async def get_station_by_id_and_owner(self, station_id: int, owner_id: int) -> Optional[Station]:
		result = await self.db.execute(select(Station).where(Station.id == station_id, Station.owner_id == owner_id))
		return result.scalar_one_or_none()

	async def create_station(self, station_data: StationCreate, owner_id: int) -> Station:
		db_station = Station(**station_data.model_dump(), owner_id=owner_id)
		self.db.add(db_station)
		await self.db.commit()
		await self.db.refresh(db_station)
		return db_station

	async def update_station(self, station: Station, update_data: StationUpdate) -> Station:
		update_dict = update_data.model_dump(exclude_unset=True)
		for key, value in update_dict.items():
			setattr(station, key, value)
		await self.db.commit()
		await self.db.refresh(station)
		return station

	async def delete_station(self, station: Station) -> None:
		await self.db.delete(station)
		await self.db.commit()
