from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Car
from app.schemas.car import CarCreate


class CarRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_cars_by_owner(self, owner_id: int) -> list[Car]:
		result = await self.db.execute(select(Car).where(Car.owner_id == owner_id))
		return list(result.scalars().all())

	async def insert_car_for_owner(self, owner_id: int, car: CarCreate) -> Car:
		result = await self.db.execute(
			select(Car).where(
				Car.owner_id == owner_id,
				Car.license_plate_number == car.license_plate_number,
			)
		)

		existing_car = result.scalar_one_or_none()
		if existing_car is not None:
			return existing_car

		db_car = Car(
			type=car.type,
			license_plate_number=car.license_plate_number,
			owner_id=owner_id,
		)

		self.db.add(db_car)
		await self.db.commit()
		await self.db.refresh(db_car)

		return db_car