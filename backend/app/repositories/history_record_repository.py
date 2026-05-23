from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HistoryRecord
from app.schemas import HistoryRecordCreate


class HistoryRecordRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_history_records_by_car(self, car_id: int) -> list[HistoryRecord]:
		result = await self.db.execute(select(HistoryRecord).where(HistoryRecord.car_id == car_id))
		return list(result.scalars().all())

	async def insert_history_record(self, history_record: HistoryRecordCreate) -> None:
		db_history_record = HistoryRecord(
			**history_record.model_dump()
		)

		self.db.add(db_history_record)
		await self.db.commit()
		await self.db.refresh(db_history_record)