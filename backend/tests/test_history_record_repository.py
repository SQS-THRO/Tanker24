# tests/repositories/test_history_record_repository.py

from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

import pytest

from app.models import HistoryRecord
from app.repositories.history_record_repository import HistoryRecordRepository
from app.schemas.history_record import HistoryRecordCreate


class TestHistoryRecordRepository:

    @pytest.fixture
    def db(self):
        db = Mock()
        db.execute = AsyncMock()
        db.commit = AsyncMock()
        db.refresh = AsyncMock()
        db.add = Mock()
        return db

    @pytest.fixture
    def history_record_create(self) -> HistoryRecordCreate:
        return HistoryRecordCreate(
            timestamp=datetime.now(UTC),
            mileage=12345.6,
            price_per_litre=1.89,
            litres=42.5,
            car_id=10,
            fuel_type_id=2,
        )

    @pytest.mark.asyncio
    async def test_get_history_records_by_car_returns_records(self, db) -> None:
        records = [
            Mock(spec=HistoryRecord),
            Mock(spec=HistoryRecord),
        ]

        scalars_result = Mock()
        scalars_result.all.return_value = records

        execute_result = Mock()
        execute_result.scalars.return_value = scalars_result

        db.execute.return_value = execute_result

        repository = HistoryRecordRepository(db)

        result = await repository.get_history_records_by_car(car_id=10)

        assert result == records
        db.execute.assert_awaited_once()
        execute_result.scalars.assert_called_once()
        scalars_result.all.assert_called_once()

    @pytest.mark.asyncio
    async def test_insert_history_record_adds_commits_and_refreshes(
        self,
        db,
        history_record_create: HistoryRecordCreate,
    ) -> None:
        repository = HistoryRecordRepository(db)

        await repository.insert_history_record(history_record_create)

        db.add.assert_called_once()
        added_record = db.add.call_args.args[0]

        assert isinstance(added_record, HistoryRecord)
        assert added_record.timestamp == history_record_create.timestamp
        assert pytest.approx(added_record.mileage) == pytest.approx(history_record_create.mileage)
        assert pytest.approx(added_record.price_per_litre) == pytest.approx(history_record_create.price_per_litre)
        assert pytest.approx(added_record.litres) == pytest.approx(history_record_create.litres)
        assert added_record.car_id == history_record_create.car_id
        assert added_record.fuel_type_id == history_record_create.fuel_type_id

        db.commit.assert_awaited_once()
        db.refresh.assert_awaited_once_with(added_record)

    @pytest.mark.asyncio
    async def test_delete_by_id_for_user_returns_true_when_deleted(self, db) -> None:
        execute_result = Mock()
        execute_result.rowcount = 1
        db.execute.return_value = execute_result

        repository = HistoryRecordRepository(db)

        result = await repository.delete_by_id_for_user(
            history_record_id=99,
            user_id=123,
        )

        assert result is True
        db.execute.assert_awaited_once()
        db.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_delete_by_id_for_user_returns_false_when_not_deleted(self, db) -> None:
        execute_result = Mock()
        execute_result.rowcount = 0
        db.execute.return_value = execute_result

        repository = HistoryRecordRepository(db)

        result = await repository.delete_by_id_for_user(
            history_record_id=99,
            user_id=123,
        )

        assert result is False
        db.execute.assert_awaited_once()
        db.commit.assert_awaited_once()