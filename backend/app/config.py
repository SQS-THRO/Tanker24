import os
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	app_name: str = "Tanker24 Backend"
	app_version: str = "1.0.0"
	debug: bool = False

	model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

	# Set default value for the database type
	db_type: str = "sqlite"

	# PostgreSQL database settings
	postgres_user: str | None = None
	postgres_password: str | None = None
	postgres_host: str | None = None
	postgres_port: int | None = 5432
	postgres_db: str | None = None

	# Public backend url setting
	public_backend_url: str | None = None

    # SQLite database settings
	# Only the database path needs to be configured
	sqlite_path: str = "./test.db"

	secret: str = ""

	jwt_lifetime_minutes: int = 60

	CORSorigins: list[str] = [
		"http://localhost:5173",
		"http://localhost:3000",
		"http://127.0.0.1:5173",
		"http://127.0.0.1:3000",
        "https://tanker24.eu",
        "https://www.tanker24.eu",
	]

	_invitation_keys: list[str] = []

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if not self.secret:
			raise ValueError("SECRET environment variable must be set!")
		if not self.db_type:
			raise ValueError("Database type DB_TYPE must be set to start the application!")

		self._parse_invitation_keys()


	@property
	def invitation_keys(self) -> list[str]:
		return self._invitation_keys


	def _parse_invitation_keys(self) -> None:
		keys_str = os.environ.get("INVITATION_KEYS", "")
		if keys_str:
			self._invitation_keys = [k.strip() for k in keys_str.split(",") if k.strip()]
			for key in self._invitation_keys:
				if not re.match(r"^[a-fA-F0-9]{32}$", key):
					raise ValueError(
						f"Invalid invitation key format: {key}. Must be a 128-bit hex string (32 characters)."
					)

	# Helper function for building the dynamic database connection string
	# Postgreql and sqlite db are supported
	# The @property decorator flags that the function returns some internal property
	@property
	def database_url(self) -> str:
		# Check if the db_type is postgresql
		if self.db_type == "postgresql":
			if not all(
                [
                    self.postgres_user,
                    self.postgres_password,
                    self.postgres_host,
					self.postgres_port,
                    self.postgres_db,
                ]
            ):
				raise ValueError(
                    "For DB_TYPE=postgresql, POSTGRES_USER, POSTGRES_PASSWORD, "
                    "POSTGRES_HOST, POSTGRES_PORT, and POSTGRES_DB must be set."
                )

			# Configure the postgresql url from the env var settings
			return (
                f"postgresql+asyncpg://{self.postgres_user}:"
                f"{self.postgres_password}@{self.postgres_host}:"
                f"{self.postgres_port}/{self.postgres_db}"
            )

		# Check if the db_type is sqllite
		if self.db_type == "sqlite":
			# Support inline memory for sqllite as well for rapid testing
			if self.sqlite_path == ":memory:":
				return "sqlite+aiosqlite:///:memory:"
			return f"sqlite+aiosqlite:///{self.sqlite_path}"
		raise ValueError(f"Unsupported DB_TYPE: {self.db_type}")


settings = Settings()
