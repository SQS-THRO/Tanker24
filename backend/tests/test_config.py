import os
from unittest.mock import patch

import pytest

from app.config import Settings


# Check if the sqllite parameters are used if the env vars match it
def test_sqlite_database_url_builds_successfully() -> None:
	settings = Settings(
		secret="test-secret",
		db_type="sqlite",
		sqlite_path="./test.db",
	)

	assert settings.database_url == "sqlite+aiosqlite:///./test.db"


# Check if the sqllite databse url is build correctly based on the desired schema
def test_sqlite_memory_database_url_builds_successfullyy() -> None:
	settings = Settings(
		secret="test-secret",
		db_type="sqlite",
		sqlite_path=":memory:",
	)

	assert settings.database_url == "sqlite+aiosqlite:///:memory:"


# check if the postgresql db connection string is being build correctly.
def test_postgresql_database_url_builds_successfully() -> None:
	settings = Settings(
		secret="test-secret",
		db_type="postgresql",
		postgres_user="TestUser",
		postgres_password="TestPassword",
		postgres_host="postgres",
		postgres_port=5432,
		postgres_db="tanker24",
	)

	assert settings.database_url == "postgresql+asyncpg://TestUser:TestPassword@postgres:5432/tanker24"


# Check if missing an env var is raising the value error correctly
def test_missing_env_var_secret_raises_value_error() -> None:
	with pytest.raises(ValueError, match="SECRET environment variable must be set!"):
		Settings(
			secret="",
			db_type="sqlite",
			sqlite_path="./test.db",
		)


# Check if missing an env var is raising the value error correctly
def test_missing_env_var_db_type_raises_value_error() -> None:
	with pytest.raises(ValueError, match="Database type DB_TYPE must be set to start the application!"):
		Settings(
			secret="Test-Secret",
			db_type="",
			postgres_user="TestUser",
			postgres_password="TestPassword",
			postgres_host="postgres",
			postgres_port=12345,
			postgres_db="tanker24",
		)


test_combinations = [
	("test-secret", "postgresql", "TestUser", "TestPassword", "postgres", 5432, ""),
	("test-secret", "postgresql", "TestUser", "TestPassword", "postgres", None, "tanker24"),
	("test-secret", "postgresql", "TestUser", "TestPassword", "", 5432, "tanker24"),
	("test-secret", "postgresql", "TestUser", "", "postgres", 5432, "tanker24"),
	("test-secret", "postgresql", "", "TestPassword", "postgres", 5432, "tanker24"),
]


# Check if missing an env var is raising the value error correctly
@pytest.mark.parametrize("secret,db_type,user,password,host,port,db", test_combinations)
def test_postgresql_missing_fields_raises_value_error(secret, db_type, user, password, host, port, db) -> None:
	settings = Settings(
		secret=secret,
		db_type=db_type,
		postgres_user=user,
		postgres_password=password,
		postgres_host=host,
		postgres_port=port,
		postgres_db=db,
	)

	with pytest.raises(
		ValueError,
		match=(
			"For DB_TYPE=postgresql, POSTGRES_USER, POSTGRES_PASSWORD, "
			"POSTGRES_HOST, POSTGRES_PORT, and POSTGRES_DB must be set."
		),
	):
		_ = settings.database_url


# Check if the filter for the supported database types is working
def test_unsupported_db_type_raises_value_error() -> None:
	settings = Settings(
		secret="test-secret",
		db_type="mysql",
	)

	with pytest.raises(ValueError, match="Unsupported DB_TYPE: mysql"):
		_ = settings.database_url


class TestCorsOrigins:
	def test_multiple_valid_origins(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "https://app.example.com,http://localhost:3000",
			},
		):
			settings = Settings()
			assert settings.cors_origins == [
				"https://app.example.com",
				"http://localhost:3000",
			]

	def test_single_valid_origin(self) -> None:
		with patch.dict(
			os.environ,
			{"SECRET": "test-secret", "CORS_ORIGINS": "https://myapp.com"},
		):
			settings = Settings()
			assert settings.cors_origins == ["https://myapp.com"]

	def test_empty_string_returns_empty_list(self) -> None:
		with patch.dict(
			os.environ,
			{"SECRET": "test-secret", "CORS_ORIGINS": ""},
		):
			settings = Settings()
			assert settings.cors_origins == []

	def test_missing_env_var_returns_empty_list(self) -> None:
		with patch.dict(
			os.environ,
			{"SECRET": "test-secret"},
			clear=True,
		):
			settings = Settings()
			assert settings.cors_origins == []

	def test_https_origin_accepted(self) -> None:
		with patch.dict(
			os.environ,
			{"SECRET": "test-secret", "CORS_ORIGINS": "https://secure.example.com"},
		):
			settings = Settings()
			assert settings.cors_origins == ["https://secure.example.com"]

	def test_http_origin_accepted(self) -> None:
		with patch.dict(
			os.environ,
			{"SECRET": "test-secret", "CORS_ORIGINS": "http://localhost:8080"},
		):
			settings = Settings()
			assert settings.cors_origins == ["http://localhost:8080"]

	def test_whitespace_around_origins_is_stripped(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "  https://example.com  ,  http://localhost:3000  ",
			},
		):
			settings = Settings()
			assert settings.cors_origins == [
				"https://example.com",
				"http://localhost:3000",
			]

	def test_trailing_comma_handled(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "https://example.com,",
			},
		):
			settings = Settings()
			assert settings.cors_origins == ["https://example.com"]

	def test_origin_with_path_accepted(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "https://example.com/subpath",
			},
		):
			settings = Settings()
			assert settings.cors_origins == ["https://example.com/subpath"]

	def test_origin_with_port_accepted(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "http://localhost:3000",
			},
		):
			settings = Settings()
			assert settings.cors_origins == ["http://localhost:3000"]

	def test_missing_protocol_raises_value_error(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "example.com",
			},
		):
			with pytest.raises(
				ValueError,
				match=r"Invalid CORS origin format: example\.com. Must be a valid URL starting with http:// or https://.",
			):
				Settings()

	def test_ftp_protocol_raises_value_error(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "ftp://example.com",
			},
		):
			with pytest.raises(
				ValueError,
				match=r"Invalid CORS origin format: ftp://example\.com. Must be a valid URL starting with http:// or https://.",
			):
				Settings()

	def test_empty_origin_after_strip_raises_value_error(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "https://valid.com, ,",
			},
		):
			settings = Settings()
			assert settings.cors_origins == ["https://valid.com"]

	def test_invalid_among_valid_raises_value_error(self) -> None:
		with patch.dict(
			os.environ,
			{
				"SECRET": "test-secret",
				"CORS_ORIGINS": "https://valid.com,not-a-url",
			},
		):
			with pytest.raises(
				ValueError,
				match=r"Invalid CORS origin format: not-a-url.",
			):
				Settings()
