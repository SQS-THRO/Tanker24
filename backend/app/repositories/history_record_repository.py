from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import HistoryRecord
from app.schemas.history_record import HistoryRecordCreate


class HistoryRecordRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	# Return the history records for a specific car
	async def get_history_records_by_car(self, car_id: int) -> list[HistoryRecord]:
		result = await self.db.execute(select(HistoryRecord).where(HistoryRecord.car_id == car_id))
		return list(result.scalars().all())

	# create a history record for a specific user and car
	async def insert_history_record(self, history_record: HistoryRecordCreate) -> None:
		db_history_record = HistoryRecord(**history_record.model_dump())

		self.db.add(db_history_record)
		await self.db.commit()
		await self.db.refresh(db_history_record)

	# Delete a specific history record for a given user
	async def delete_by_id_for_user(
		self,
		history_record_id: int,
		user_id: int,
	) -> bool:
		stmt = (
			delete(HistoryRecord)
			.where(
				HistoryRecord.id == history_record_id,
				HistoryRecord.car.has(owner_id=user_id),
			)
        	.returning(HistoryRecord.id)
		)

		result = await self.db.execute(stmt)
		deleted_id = result.scalar_one_or_none()

		await self.db.commit()

		# make sure that something actually changed
		return deleted_id is not None