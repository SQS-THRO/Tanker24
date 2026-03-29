import os
import re

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
	model_config = SettingsConfigDict(
		env_file=".env",
		env_file_encoding="utf-8",
	)

	app_name: str = "Tanker24 Backend"
	app_version: str = "1.0.0"
	debug: bool = False

	database_url: str = "sqlite+aiosqlite:///./data.db"
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
			raise ValueError("SECRET environment variable must be set")
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


settings = Settings()
