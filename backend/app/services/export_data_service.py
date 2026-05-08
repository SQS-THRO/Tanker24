import logging
from abc import ABC, abstractmethod
from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.car_repository import CarRepository
from app.repositories.history_record_repository import HistoryRecordRepository

logger = logging.getLogger("app.export_data_service")


class ExportDataService(ABC):
	def __init__(self, db: AsyncSession) -> None: ...

	@abstractmethod
	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]: ...


class NestedExportDataService(ExportDataService):
	def __init__(self, db: AsyncSession):
		self.car_repo = CarRepository(db)
		self.history_repo = HistoryRecordRepository(db)
		self.db = db

	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]:
		try:
			cars = await self.car_repo.get_cars_by_owner(user_id)

			result = []

			for car in cars:
				history_records = await self.history_repo.get_history_records_by_car(car.id)
				history = []
				if len(history_records) > 0:
					for record in history_records:
						history.append(
							{
								"id": record.id,
								"car_id": record.car_id,
								"created_at": record.timestamp,
								"mileage": record.mileage,
								"price_per_litre": record.price_per_litre,
								"litres": record.litres,
								"total_price": record.price_per_litre * record.litres,
								"fuel_type": record.fuel_type.name,
							}
						)
				result.append(
					{
						"id": car.id,
						"type": car.type,
						"license_plate_number": car.license_plate_number,
						"history": history,
					}
				)

			return result

		except SQLAlchemyError as e:
			logger.exception("Database error during nested export for user_id=%d", user_id)
			await self.db.rollback()
			raise HTTPException(
				status_code=503,
				detail="Database temporarily unavailable.",
			) from e


class FlatExportDataService(ExportDataService):
	def __init__(self, db: AsyncSession):
		self.car_repo = CarRepository(db)
		self.history_repo = HistoryRecordRepository(db)
		self.db = db

	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]:
		try:
			result = []
			cars = await self.car_repo.get_cars_by_owner(user_id)
			for car in cars:
				history_records = await self.history_repo.get_history_records_by_car(car.id)
				if len(history_records) > 0:
					for record in history_records:
						result.append(
							{
								"id": record.id,
								"car_id": record.car_id,
								"car_type": car.type,
								"license_plate_number": car.license_plate_number,
								"created_at": record.timestamp,
								"mileage": record.mileage,
								"price_per_litre": record.price_per_litre,
								"litres": record.litres,
								"total_price": record.price_per_litre * record.litres,
								"fuel_type": record.fuel_type.name,
							}
						)

			return result
		except SQLAlchemyError as e:
			logger.exception("Database error during flat export for user_id=%d", user_id)
			await self.db.rollback()
			raise HTTPException(
				status_code=503,
				detail="Database temporarily unavailable.",
			) from e
