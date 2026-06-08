import pytest
from datetime import datetime, UTC

from sqlalchemy import select

from app.models import Station
from app.repositories.station_repository import StationRepository


class TestStationRepositoryDelete:
	@pytest.mark.asyncio
	async def test_delete_by_tankerkoenig_ids_deletes_matching_stations(self, test_db_session):
		now = datetime.now(UTC).replace(tzinfo=None)
		stations = [
			Station(
				tankerkoenig_id="id-1",
				name="Station 1",
				brand="Brand A",
				latitude=1.0,
				longitude=1.0,
				cached_at=now,
			),
			Station(
				tankerkoenig_id="id-2",
				name="Station 2",
				brand="Brand B",
				latitude=2.0,
				longitude=2.0,
				cached_at=now,
			),
			Station(
				tankerkoenig_id="id-3",
				name="Station 3",
				brand="Brand C",
				latitude=3.0,
				longitude=3.0,
				cached_at=now,
			),
		]
		for s in stations:
			test_db_session.add(s)
		await test_db_session.commit()

		repo = StationRepository(test_db_session)
		await repo.delete_by_tankerkoenig_ids({"id-1", "id-3"})

		result = await test_db_session.execute(select(Station))
		remaining = result.scalars().all()
		assert len(remaining) == 1
		assert remaining[0].tankerkoenig_id == "id-2"

	@pytest.mark.asyncio
	async def test_delete_by_tankerkoenig_ids_empty_set_does_nothing(self, test_db_session):
		now = datetime.now(UTC).replace(tzinfo=None)
		station = Station(
			tankerkoenig_id="keep-me",
			name="Keep Me",
			brand="Brand",
			latitude=1.0,
			longitude=1.0,
			cached_at=now,
		)
		test_db_session.add(station)
		await test_db_session.commit()

		repo = StationRepository(test_db_session)
		await repo.delete_by_tankerkoenig_ids(set())

		result = await test_db_session.execute(select(Station))
		remaining = result.scalars().all()
		assert len(remaining) == 1
		assert remaining[0].tankerkoenig_id == "keep-me"

	@pytest.mark.asyncio
	async def test_delete_by_tankerkoenig_ids_no_matches(self, test_db_session):
		now = datetime.now(UTC).replace(tzinfo=None)
		station = Station(
			tankerkoenig_id="only-one",
			name="Only One",
			brand="Brand",
			latitude=1.0,
			longitude=1.0,
			cached_at=now,
		)
		test_db_session.add(station)
		await test_db_session.commit()

		repo = StationRepository(test_db_session)
		await repo.delete_by_tankerkoenig_ids({"nonexistent-id"})

		result = await test_db_session.execute(select(Station))
		remaining = result.scalars().all()
		assert len(remaining) == 1
