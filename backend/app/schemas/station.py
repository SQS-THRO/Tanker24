from pydantic import BaseModel, ConfigDict
from datetime import datetime


class StationBase(BaseModel):
	tankerkoenig_id: str
	name: str
	brand: str
	street: str | None = None
	house_number: str | None = None
	post_code: int | None = None
	place: str | None = None
	latitude: float
	longitude: float
	distance: float | None = None
	diesel: float | None = None
	e5: float | None = None
	e10: float | None = None
	is_open: bool = True


class Station(StationBase):
	id: int
	cached_at: datetime
	cache_lat: float | None = None
	cache_lon: float | None = None
	cache_radius: float | None = None

	model_config = ConfigDict(from_attributes=True)
