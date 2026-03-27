from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

import pytest
from unittest.mock import Mock, AsyncMock

from app.auth import CustomUserManager
from app.auth import get_user_db
from app.models import User
from app.schemas.user import UserRead


class TestAuthEndpoints:
	TEST_PASSWORD = "test-password"

	@pytest.fixture
	def mock_user_db(self):
		return AsyncMock()

	@pytest.fixture
	def user_manager(self, mock_user_db):
		return CustomUserManager(mock_user_db)

	@pytest.fixture
	def user(self):
		return UserRead(
			id=1,
			email="test@example.com",
			forename="Max",
			surname="Mustermann",
			pin="1234",
			is_active=True,
			is_superuser=False,
			is_verified=False,
			hashed_password=self.TEST_PASSWORD,
		)

	@pytest.mark.asyncio
	async def test_on_after_register_returns_none(self, user_manager, user):
		result = await user_manager.on_after_register(user)
		assert result is None

	@pytest.mark.asyncio
	async def test_on_after_register_with_request_returns_none(self, user_manager, user):
		request = Mock()
		result = await user_manager.on_after_register(user, request)
		assert result is None

	def test_get_user_db_returns_sqlalchemy_user_database(self, test_db_session):
		user_db = get_user_db(test_db_session)

		# Test that the db instance exists, the user table is actually returned and that the sessions is a user db session
		assert isinstance(user_db, SQLAlchemyUserDatabase)
		assert user_db.session is test_db_session
		assert user_db.user_table is User
