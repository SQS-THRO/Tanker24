import os
import pytest
import pytest_asyncio
from unittest.mock import patch

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings
from app.invitation_keys import sync_invitation_keys
from app.models import Base, InvitationKey, User


class TestSyncInvitationKeys:
	@pytest_asyncio.fixture
	async def session(self):
		engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
		async with engine.begin() as conn:
			await conn.run_sync(Base.metadata.create_all)
		async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
		async with async_session() as session:
			yield session
		await engine.dispose()

	@pytest.mark.asyncio
	async def test_sync_adds_new_keys(self, session: AsyncSession):
		with patch("app.invitation_keys.settings") as mock_settings:
			mock_settings.invitation_keys = ["a" * 32, "b" * 32]
			await sync_invitation_keys(session)

		result = await session.execute(select(InvitationKey))
		keys = result.scalars().all()
		assert len(keys) == 2
		keys_set = {k.key for k in keys}
		assert "a" * 32 in keys_set
		assert "b" * 32 in keys_set

	@pytest.mark.asyncio
	async def test_sync_removes_deleted_keys(self, session: AsyncSession):
		session.add(InvitationKey(key="a" * 32))
		session.add(InvitationKey(key="b" * 32))
		await session.commit()

		with patch("app.invitation_keys.settings") as mock_settings:
			mock_settings.invitation_keys = ["a" * 32]
			await sync_invitation_keys(session)

		result = await session.execute(select(InvitationKey))
		keys = result.scalars().all()
		assert len(keys) == 1
		assert keys[0].key == "a" * 32

	@pytest.mark.asyncio
	async def test_sync_preserves_users_when_key_deleted(self, session: AsyncSession):
		key = InvitationKey(key="a" * 32)
		session.add(key)
		await session.commit()
		await session.refresh(key)

		user = User(
			email="test@example.com",
			hashed_password="$2b$12$test",
			forename="Test",
			surname="User",
			pin="1234",
			invitation_key_id=key.id,
		)
		session.add(user)
		await session.commit()

		with patch("app.invitation_keys.settings") as mock_settings:
			mock_settings.invitation_keys = []
			await sync_invitation_keys(session)

		result = await session.execute(select(InvitationKey))
		keys = result.scalars().all()
		assert len(keys) == 0

		result = await session.execute(select(User))
		users = result.scalars().all()
		assert len(users) == 1
		assert users[0].invitation_key_id is None

	@pytest.mark.asyncio
	async def test_sync_no_changes_when_keys_match(self, session: AsyncSession):
		session.add(InvitationKey(key="a" * 32))
		await session.commit()

		with patch("app.invitation_keys.settings") as mock_settings:
			mock_settings.invitation_keys = ["a" * 32]
			await sync_invitation_keys(session)

		result = await session.execute(select(InvitationKey))
		keys = result.scalars().all()
		assert len(keys) == 1
		assert keys[0].key == "a" * 32


class TestInvitationKeyConfig:
	def test_valid_32char_hex_keys(self):
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"INVITATION_KEYS": "abcdef1234567890abcdef1234567890,00112233445566778899aabbccddeeff",
			},
		):
			settings = Settings()
			assert len(settings.invitation_keys) == 2
			assert "abcdef1234567890abcdef1234567890" in settings.invitation_keys
			assert "00112233445566778899aabbccddeeff" in settings.invitation_keys

	def test_valid_single_key(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": "a" * 32}):
			settings = Settings()
			assert len(settings.invitation_keys) == 1
			assert settings.invitation_keys[0] == "a" * 32

	def test_empty_keys_string(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": ""}):
			settings = Settings()
			assert settings.invitation_keys == []

	def test_invalid_key_too_short(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": "abc123"}):
			with pytest.raises(ValueError, match="Invalid invitation key format"):
				Settings()

	def test_invalid_key_not_hex(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": "gggggggggggggggggggggggggggggggg"}):
			with pytest.raises(ValueError, match="Invalid invitation key format"):
				Settings()

	def test_invalid_key_wrong_length(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": "a" * 31}):
			with pytest.raises(ValueError, match="Invalid invitation key format"):
				Settings()

	def test_invalid_key_too_long(self):
		with patch.dict(os.environ, {"SECRET": "test-secret", "INVITATION_KEYS": "a" * 33}):
			with pytest.raises(ValueError, match="Invalid invitation key format"):
				Settings()

	def test_keys_with_whitespace(self):
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"INVITATION_KEYS": "  abcdef1234567890abcdef1234567890  ,  00112233445566778899aabbccddeeff  ",
			},
		):
			settings = Settings()
			assert len(settings.invitation_keys) == 2
			assert "abcdef1234567890abcdef1234567890" in settings.invitation_keys
			assert "00112233445566778899aabbccddeeff" in settings.invitation_keys
