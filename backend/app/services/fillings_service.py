from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.filling_dto import FillingDTO
from app.exceptions.exceptions import FillingNotFoundException
from app.repositories.car_repository import CarRepository
from app.repositories.fuel_type_repository import FuelTypeRepository
from app.repositories.history_record_repository import HistoryRecordRepository
from app.schemas.car import CarCreate
from app.schemas.user import UserRead
from app.schemas.history_record import HistoryRecordCreate, HistoryRecord


class FillingsService:
	def __init__(self, db: AsyncSession):
		self.car_repo = CarRepository(db)
		self.history_repo = HistoryRecordRepository(db)
		self.fuel_type_repository = FuelTypeRepository(db)
		self.db = db

	async def save_history_record(self, filling: FillingDTO, user: UserRead) -> None:
		car_create = CarCreate(
			type=filling.car_type,
			license_plate_number=filling.license_plate_number,
		)

		saved_car = await self.car_repo.insert_car_for_owner(
			owner_id=user.id,
			car=car_create,
		)

		db_fuel_type = await self.fuel_type_repository.get_by_name(filling.fuel_type)

		history_record_create = HistoryRecordCreate(
			timestamp=filling.timestamp,
			mileage=filling.mileage,
			price_per_litre=filling.price_per_litre,
			litres=filling.litres,
			car_id=saved_car.id,
			fuel_type_id=db_fuel_type.id,
		)

		await self.history_repo.insert_history_record(history_record_create)

	async def delete_history_record(
			self,
			history_record_id: int,
			user: UserRead,
	) -> None:
		deleted = await self.history_repo.delete_by_id_for_user(
			history_record_id=history_record_id,
			user_id=user.id,
		)

		if not deleted:
			raise FillingNotFoundException(history_record_id)

	async def get_history_records_for_user(self, user: UserRead)->List[HistoryRecord]:
		cars = await self.car_repo.get_cars_by_owner(user.id)

		result = []

		for car in cars:
			history_records = await self.history_repo.get_history_records_by_car(car.id)
			result.append(history_records)

		return result