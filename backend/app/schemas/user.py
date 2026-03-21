from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
	email: str
	forename: str
	surname: str
	pin: str


class UserRead(UserBase):
	id: int
	is_active: bool
	is_superuser: bool
	is_verified: bool

	model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
	password: str

	def create_update_dict(self) -> dict:
		return self.model_dump()


class UserUpdate(BaseModel):
	email: str | None = None
	forename: str | None = None
	surname: str | None = None
	pin: str | None = None
	password: str | None = None
