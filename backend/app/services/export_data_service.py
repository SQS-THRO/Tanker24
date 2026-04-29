from abc import ABC, abstractmethod
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HistoryRecord, Car


class ExportDataService(ABC):
	def __init__(self, db: AsyncSession) -> None: ...

	@abstractmethod
	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]: ...


class NestedExportDataService(ExportDataService):
	def __init__(self, db: AsyncSession):
		self.db = db

	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]:
		try:
			cars_result = await self.db.execute(select(Car).where(Car.owner_id == user_id))
			cars = cars_result.scalars().all()

			result = []

			for car in cars:
				history = []
				history_query_result = await self.db.execute(
					select(HistoryRecord).where(HistoryRecord.car_id == car.id)
				)
				history_records = history_query_result.scalars().all()
				# Check if the car has any history records before processing
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
			await self.db.rollback()
			raise HTTPException(
				status_code=503,
				detail="Database temporarily unavailable.",
			) from e


class FlatExportDataService(ExportDataService):
	def __init__(self, db: AsyncSession):
		self.db = db

	async def get_user_data(self, user_id: int) -> list[dict[str, Any]]:
		try:
			result = []
			car_query_result = await self.db.execute(select(Car).where(Car.owner_id == user_id))
			cars = car_query_result.scalars().all()
			for car in cars:
				history_query_result = await self.db.execute(
					select(HistoryRecord).where(HistoryRecord.car_id == car.id)
				)
				history_records = history_query_result.scalars().all()
				# Check if the car has any history records before processing
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
			await self.db.rollback()
			raise HTTPException(
				status_code=503,
				detail="Database temporarily unavailable.",
			) from e
