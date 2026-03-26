from pydantic import BaseModel, ConfigDict, Field


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
