from pydantic import BaseModel, ConfigDict


class StationBase(BaseModel):
	name: str
	description: str | None = None


class StationCreate(StationBase):
	pass


class StationUpdate(BaseModel):
	name: str | None = None
	description: str | None = None


class Station(StationBase):
	id: int
	owner_id: int

	model_config = ConfigDict(from_attributes=True)
