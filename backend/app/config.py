from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_name: str = "Tanker24 Backend"
	app_version: str = "1.0.0"
	debug: bool = False

	database_url: str = "sqlite+aiosqlite:///./data.db"
	secret: str = ""

	jwt_lifetime_minutes: int = 60

	tankerkoenig_api_key: str = "00000000-0000-0000-0000-000000000002"
	tankerkoenig_rate_limit_per_minute: int = 100
	station_cache_expiry_minutes: int = 30
	tankerkoenig_search_radius_km: float = 5.0

	CORSorigins: list[str] = [
		"http://localhost:5173",
		"http://localhost:3000",
		"http://127.0.0.1:5173",
		"http://127.0.0.1:3000",
	]

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if not self.secret:
			raise ValueError("SECRET environment variable must be set")


settings = Settings()
