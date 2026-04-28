from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class StationBase(BaseModel):
	name: str = Field(min_length=1)
	description: str | None = None
	latitude: float | None = None
	longitude: float | None = None


class StationCreate(StationBase):
	pass


class StationUpdate(BaseModel):
	name: str | None = None
	description: str | None = None
	latitude: float | None = None
	longitude: float | None = None


class Station(StationBase):
	id: int
	owner_id: int

	model_config = ConfigDict(from_attributes=True)


class TankerkoenigStationBase(BaseModel):
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


class TankerkoenigStation(TankerkoenigStationBase):
	id: int
	cached_at: datetime
	cache_lat: float | None = None
	cache_lon: float | None = None
	cache_radius: float | None = None

	model_config = ConfigDict(from_attributes=True)
