from pydantic import BaseModel, ConfigDict


class UserRead(BaseModel):
    id: int
    email: str
    is_active: bool
    is_superuser: bool
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    email: str | None = None
    password: str | None = None
