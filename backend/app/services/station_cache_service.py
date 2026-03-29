import asyncio
import json
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session_maker
from app.dtos.gas_station_dtos import GasStation
from app.models import TankerkoenigStation
from app.services.gas_station_service import TankerkoenigGasStationService
from app.services.rate_limiter import global_rate_limiter


class WebSocketManager:
	def __init__(self):
		self._connections: set[asyncio.Queue] = set()
		self._lock = asyncio.Lock()

	async def connect(self) -> asyncio.Queue:
		queue: asyncio.Queue = asyncio.Queue()
		async with self._lock:
			self._connections.add(queue)
		return queue

	async def disconnect(self, queue: asyncio.Queue) -> None:
		async with self._lock:
			self._connections.discard(queue)

	async def broadcast(self, message: dict[str, Any]) -> None:
		async with self._lock:
			connections_snapshot = list(self._connections)

		if not connections_snapshot:
			return

		message_json = json.dumps(message)
		for queue in connections_snapshot:
			try:
				queue.put_nowait(message_json)
			except asyncio.QueueFull:
				pass


ws_manager = WebSocketManager()


class StationCacheService:
	def __init__(self):
		self.gas_station_service = TankerkoenigGasStationService(
			api_key=settings.tankerkoenig_api_key
		)
		self._queue: asyncio.Queue[tuple[float, float, asyncio.Queue | None]] = asyncio.Queue()
		self._processing = False
		self._lock = asyncio.Lock()

	async def enqueue_request(
		self,
		lat: float,
		lon: float,
		response_queue: asyncio.Queue | None = None
	) -> None:
		await self._queue.put((lat, lon, response_queue))
		await self._start_processing()

	async def _start_processing(self) -> None:
		async with self._lock:
			if self._processing:
				return
			self._processing = True

		try:
			while True:
				try:
					lat, lon, response_queue = self._queue.get_nowait()
				except asyncio.QueueEmpty:
					break

				await self._process_request(lat, lon, response_queue)
		finally:
			async with self._lock:
				self._processing = False

	async def _process_request(
		self,
		lat: float,
		lon: float,
		response_queue: asyncio.Queue | None
	) -> None:
		await ws_manager.broadcast({
			"type": "caching_stations",
			"lat": lat,
			"lon": lon
		})

		if response_queue:
			try:
				await response_queue.put({"type": "caching_stations", "lat": lat, "lon": lon})
			except asyncio.QueueFull:
				pass

		try:
			await global_rate_limiter.wait_for_token()
			stations = self.gas_station_service.get_gas_stations(
				latitude=lat,
				longitude=lon,
				radius=settings.tankerkoenig_search_radius_km
			)
		except Exception as e:
			error_message = str(e)
			await ws_manager.broadcast({
				"type": "error",
				"message": error_message
			})
			if response_queue:
				try:
					await response_queue.put({"type": "error", "message": error_message})
				except asyncio.QueueFull:
					pass
			return

		async with async_session_maker() as db:
			for station in stations:
				await self._upsert_station(db, station)

		if response_queue:
			try:
				await response_queue.put({"type": "complete", "lat": lat, "lon": lon})
			except asyncio.QueueFull:
				pass

	async def _upsert_station(self, db: AsyncSession, station: GasStation) -> None:
		expiry_time = datetime.utcnow() - timedelta(minutes=settings.station_cache_expiry_minutes)

		result = await db.execute(
			select(TankerkoenigStation).where(
				TankerkoenigStation.tankerkoenig_id == station.id
			)
		)
		existing = result.scalar_one_or_none()

		is_new = existing is None
		is_updated = False

		if existing:
			if existing.cached_at < expiry_time:
				is_updated = True
				existing.name = station.name
				existing.brand = station.brand
				existing.street = station.street
				existing.house_number = station.house_number
				existing.post_code = station.post_code
				existing.place = station.place
				existing.latitude = station.latitude
				existing.longitude = station.longitude
				existing.distance = station.distance
				existing.diesel = station.diesel
				existing.e5 = station.e5
				existing.e10 = station.e10
				existing.is_open = station.is_open
				existing.cached_at = datetime.utcnow()
		else:
			new_station = TankerkoenigStation(
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
				cached_at=datetime.utcnow()
			)
			db.add(new_station)

		await db.commit()

		if is_new:
			await ws_manager.broadcast({
				"type": "new_station",
				"name": station.name,
				"brand": station.brand,
				"lat": station.latitude,
				"lon": station.longitude
			})
		elif is_updated:
			await ws_manager.broadcast({
				"type": "updated_station",
				"name": station.name,
				"brand": station.brand,
				"lat": station.latitude,
				"lon": station.longitude
			})


station_cache_service = StationCacheService()
