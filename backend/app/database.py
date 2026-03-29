from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
	AsyncSession,
	async_sessionmaker,
	create_async_engine,
)

from app.config import settings
from app.models import Base

is_sqlite = settings.db_type == "sqlite"

engine = create_async_engine(
	settings.database_url,
	echo=settings.debug,
    connect_args={"check_same_thread": False} if is_sqlite else {},
)

async_session_maker = async_sessionmaker(
	engine,
	class_=AsyncSession,
	expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async with async_session_maker() as session:
		yield session


async def init_db() -> None:
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)
