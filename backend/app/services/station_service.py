from typing import List, Optional

from app.models import Station
from app.repositories.station_repository import StationRepository
from app.schemas.station import StationCreate, StationUpdate


class StationService:
	def __init__(self, repository: StationRepository) -> None:
		self.repository = repository

	async def get_stations_by_owner(self, owner_id: int) -> List[Station]:
		return await self.repository.get_stations_by_owner(owner_id)

	async def get_station_by_id_and_owner(self, station_id: int, owner_id: int) -> Optional[Station]:
		return await self.repository.get_station_by_id_and_owner(station_id, owner_id)

	async def create_station(self, station_data: StationCreate, owner_id: int) -> Station:
		return await self.repository.create_station(station_data, owner_id)

	async def update_station(self, station: Station, update_data: StationUpdate) -> Station:
		return await self.repository.update_station(station, update_data)

	async def delete_station(self, station: Station) -> None:
		await self.repository.delete_station(station)
