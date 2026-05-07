from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HistoryRecord


class HistoryRecordRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_history_records_by_car(self, car_id: int) -> list[HistoryRecord]:
		result = await self.db.execute(select(HistoryRecord).where(HistoryRecord.car_id == car_id))
		return list(result.scalars().all())
