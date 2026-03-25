import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_SECRET = "test-secret-key-for-testing-only"

if not os.environ.get("SECRET"):
	os.environ["SECRET"] = TEST_SECRET

from app.auth import get_jwt_strategy
from app.database import get_db
from app.main import app
from app.models import Base, Station, User


@pytest_asyncio.fixture
async def test_engine():
	engine = create_async_engine(
		"sqlite+aiosqlite:///:memory:",
		echo=False,
	)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
	yield engine
	await engine.dispose()


@pytest_asyncio.fixture
async def test_db_session(test_engine):
	async_session = async_sessionmaker(
		test_engine,
		class_=AsyncSession,
		expire_on_commit=False,
	)
	async with async_session() as session:
		yield session
		await session.rollback()


@pytest_asyncio.fixture
async def async_client(test_db_session):
	async def override_get_db():
		yield test_db_session

	app.dependency_overrides[get_db] = override_get_db

	async with AsyncClient(
		transport=ASGITransport(app=app),
		base_url="http://test",
	) as client:
		yield client

	app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db_session):
	user = User(
		email="test@example.com",
		hashed_password="$2b$12$test_hash_for_password_123456789012",
		forename="Test",
		surname="User",
		pin="1234",
		is_active=True,
		is_verified=True,
	)
	test_db_session.add(user)
	await test_db_session.commit()
	await test_db_session.refresh(user)
	return user


@pytest_asyncio.fixture
async def authenticated_client(async_client, test_user):
	strategy = get_jwt_strategy()
	token = await strategy.write_token(test_user)
	async_client.headers["Authorization"] = f"Bearer {token}"
	return async_client


@pytest_asyncio.fixture
async def second_user(test_db_session):
	user = User(
		email="second@example.com",
		hashed_password="$2b$12$test_hash_for_password_987654321098",
		forename="Second",
		surname="User",
		pin="5678",
		is_active=True,
		is_verified=True,
	)
	test_db_session.add(user)
	await test_db_session.commit()
	await test_db_session.refresh(user)
	return user


@pytest.fixture
def station_data():
	return {
		"name": "Test Station",
		"description": "A test gas station",
	}


@pytest.fixture
def station_update_data():
	return {
		"name": "Updated Station Name",
		"description": "Updated description",
	}


@pytest_asyncio.fixture
async def owned_station(test_db_session, test_user, station_data):
	station = Station(**station_data, owner_id=test_user.id)
	test_db_session.add(station)
	await test_db_session.commit()
	await test_db_session.refresh(station)
	return station


@pytest_asyncio.fixture
async def other_user_station(test_db_session, second_user):
	station = Station(
		name="Other User Station",
		description="Station owned by second user",
		owner_id=second_user.id,
	)
	test_db_session.add(station)
	await test_db_session.commit()
	await test_db_session.refresh(station)
	return station
