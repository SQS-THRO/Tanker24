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

    assert (
        settings.database_url
        == "postgresql+asyncpg://TestUser:TestPassword@postgres:5432/tanker24"
    )

# Check if missing an env var is raising the value error correctly
def test_missing_env_var_secret_raises_value_error() -> None:
    with pytest.raises(ValueError, match="SECRET environment variable must be set!"):
        Settings(
            secret = "",
            db_type="sqlite",
            sqlite_path="./test.db",
        )

# Check if missing an env var is raising the value error correctly
def test_missing_env_var_db_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="Database type DB_TYPE must be set to start the application!"):
        Settings(
            secret = "Test-Secret",
            sqlite_path="./test.db",
        )


test_combinations = [
    ("test-secret","postgresql", "TestUser","TestPassword","postgres",5432, ""),
("test-secret","postgresql", "TestUser","TestPassword","postgres", None, "tanker24"),
("test-secret","postgresql", "TestUser","TestPassword","",5432, "tanker24"),
("test-secret","postgresql", "TestUser","","postgres",5432, "tanker24"),
("test-secret","postgresql", "","TestPassword","postgres",5432, "tanker24"),
]

# Check if missing an env var is raising the value error correctly
@pytest.mark.parametrize("secret,db_type,user,password,host,port,db", test_combinations)
def test_postgresql_missing_fields_raises_value_error(secret,db_type,user,password,host,port,db) -> None:
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