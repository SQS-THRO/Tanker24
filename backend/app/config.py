from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	app_name: str = "Tanker24 Backend"
	app_version: str = "1.0.0"
	debug: bool = False

	database_url: str = "sqlite+aiosqlite:///./data.db"
	secret: str = ""

	jwt_lifetime_minutes: int = 60

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"

	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		if not self.secret:
			raise ValueError("SECRET environment variable must be set")


settings = Settings()
