from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from fastapi_users.exceptions import InvalidPasswordException

import pytest
from unittest.mock import Mock, AsyncMock

from app.auth import CustomUserManager
from app.auth import get_user_db
from app.models import User
from app.schemas.user import UserRead


class TestPasswordValidation:
	VALID_PASSWORD = "Test1234!"

	@pytest.fixture
	def mock_user_db(self):
		return AsyncMock()

	@pytest.fixture
	def user_manager(self, mock_user_db):
		return CustomUserManager(mock_user_db)

	@pytest.mark.asyncio
	async def test_valid_password_all_criteria(self, user_manager):
		await user_manager.validate_password(self.VALID_PASSWORD)

	@pytest.mark.asyncio
	async def test_password_too_short(self, user_manager):
		with pytest.raises(InvalidPasswordException) as exc_info:
			await user_manager.validate_password("Test1!a")
		assert "at least 8 characters" in exc_info.value.reason

	@pytest.mark.asyncio
	async def test_password_missing_uppercase(self, user_manager):
		with pytest.raises(InvalidPasswordException) as exc_info:
			await user_manager.validate_password("test1234!")
		assert "uppercase letter" in exc_info.value.reason

	@pytest.mark.asyncio
	async def test_password_missing_lowercase(self, user_manager):
		with pytest.raises(InvalidPasswordException) as exc_info:
			await user_manager.validate_password("TEST1234!")
		assert "lowercase letter" in exc_info.value.reason

	@pytest.mark.asyncio
	async def test_password_missing_number(self, user_manager):
		with pytest.raises(InvalidPasswordException) as exc_info:
			await user_manager.validate_password("TestAbcd!")
		assert "number" in exc_info.value.reason

	@pytest.mark.asyncio
	async def test_password_missing_special(self, user_manager):
		with pytest.raises(InvalidPasswordException) as exc_info:
			await user_manager.validate_password("TestAbcd1")
		assert "special character" in exc_info.value.reason

	@pytest.mark.asyncio
	async def test_password_edge_case_exactly_8_chars(self, user_manager):
		await user_manager.validate_password("Test1!Aa")

	@pytest.mark.asyncio
	async def test_password_with_various_special_chars(self, user_manager):
		for special in '!@#$%^&*(),.?":{}|<>':
			password = f"Test1234{special}"
			await user_manager.validate_password(password)


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


class TestCreateUser:
	VALID_PASSWORD = "Test1234!"

	@pytest.fixture
	def mock_user_db(self):
		return AsyncMock()

	@pytest.fixture
	def user_manager(self, mock_user_db):
		return CustomUserManager(mock_user_db)

	@pytest.fixture
	def user_create(self):
		from app.schemas.user import UserCreate

		return UserCreate(
			email="existing@example.com",
			password=self.VALID_PASSWORD,
			forename="Existing",
			surname="User",
		)

	@pytest.mark.asyncio
	async def test_create_raises_user_already_exists(self, user_manager, user_create):
		from fastapi_users.exceptions import UserAlreadyExists

		with pytest.raises(UserAlreadyExists):
			await user_manager.create(user_create)


class TestGetCurrentUser:
	def test_get_current_user_returns_user_read(self, test_db_session, test_user):
		from app.auth import get_current_user

		result = get_current_user(test_user)

		assert isinstance(result, UserRead)
		assert result.id == test_user.id
		assert result.email == test_user.email
		assert result.forename == test_user.forename
		assert result.surname == test_user.surname
		assert result.is_active == test_user.is_active
		assert result.is_superuser == test_user.is_superuser
		assert result.is_verified == test_user.is_verified

	def test_get_current_active_user_returns_user_read(self, test_db_session, test_user):
		from app.auth import get_current_active_user

		result = get_current_active_user(test_user)

		assert isinstance(result, UserRead)
		assert result.id == test_user.id
		assert result.email == test_user.email

	def test_get_current_superuser_returns_user_read(self, test_db_session, second_user):
		from app.auth import get_current_superuser

		second_user.is_superuser = True
		result = get_current_superuser(second_user)

		assert isinstance(result, UserRead)
		assert result.id == second_user.id
		assert result.email == second_user.email
		assert result.is_superuser is True
