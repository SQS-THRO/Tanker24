from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Car


class CarRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_cars_by_owner(self, owner_id: int) -> list[Car]:
		result = await self.db.execute(select(Car).where(Car.owner_id == owner_id))
		return list(result.scalars().all())
