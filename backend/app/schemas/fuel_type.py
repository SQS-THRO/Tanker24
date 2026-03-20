from pydantic import BaseModel, ConfigDict


class FuelTypeBase(BaseModel):
	name: str


class FuelTypeCreate(FuelTypeBase):
	pass


class FuelTypeUpdate(BaseModel):
	name: str | None = None


class FuelType(FuelTypeBase):
	id: int

	model_config = ConfigDict(from_attributes=True)
