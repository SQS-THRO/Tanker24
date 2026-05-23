from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.filling_dto import FillingDTO
from app.repositories.car_repository import CarRepository
from app.repositories.history_record_repository import HistoryRecordRepository
from app.schemas.car import CarCreate
from app.schemas.user import UserRead
from app.schemas.history_record import HistoryRecordCreate


class FillingsService:
	def __init__(self, db: AsyncSession):
		self.car_repo = CarRepository(db)
		self.history_repo = HistoryRecordRepository(db)
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

		history_record_create = HistoryRecordCreate(
			timestamp=filling.timestamp,
			mileage=filling.mileage,
			price_per_litre=filling.price_per_litre,
			litres=filling.litres,
			car_id=saved_car.id,
			fuel_type_id=filling.fuel_type.id,
		)

		await self.history_repo.insert_history_record(history_record_create)
