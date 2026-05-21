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
from app.models import Base, User
from datetime import datetime, UTC


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
		is_active=True,
		is_verified=True,
	)
	test_db_session.add(user)
	await test_db_session.commit()
	await test_db_session.refresh(user)
	return user


@pytest_asyncio.fixture
async def cached_station(test_db_session):
	from app.models import Station

	now = datetime.now(UTC).replace(tzinfo=None)
	station = Station(
		tankerkoenig_id="test-uuid-123",
		name="Cached Station",
		brand="Shell",
		street="Main St",
		house_number="1",
		post_code=10115,
		place="Berlin",
		latitude=52.52,
		longitude=13.405,
		distance=0.5,
		diesel=1.65,
		e5=1.75,
		e10=1.70,
		is_open=True,
		cached_at=now,
		cache_lat=52.52,
		cache_lon=13.405,
		cache_radius=5.0,
	)
	test_db_session.add(station)
	await test_db_session.commit()
	await test_db_session.refresh(station)
	return station
