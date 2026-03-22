from fastapi import Depends, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
	AuthenticationBackend,
	BearerTransport,
	JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead


class CustomUserManager(BaseUserManager[User, int]):
	user_read_model = UserRead
	user_create_model = UserCreate

	async def on_after_register(self, user: User, request: Request | None = None) -> None:
		pass

	def parse_id(self, normalized_id: str) -> int:
		return int(normalized_id)


def get_user_db(
	session: AsyncSession = Depends(get_db),
) -> SQLAlchemyUserDatabase[User, int]:
	return SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
	user_db: SQLAlchemyUserDatabase[User, int] = Depends(get_user_db),
):
	yield CustomUserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
	return JWTStrategy(
		secret=settings.secret,
		lifetime_seconds=settings.jwt_lifetime_minutes * 60,
	)


auth_backend = AuthenticationBackend(
	name="jwt",
	transport=bearer_transport,
	get_strategy=get_jwt_strategy,
)


fastapi_users = FastAPIUsers[User, int](
	get_user_manager,
	[auth_backend],
)


async def get_current_user(
	user: User = Depends(fastapi_users.current_user(active=True)),
) -> User:
	return user


async def get_current_active_user(
	user: User = Depends(fastapi_users.current_user(active=True)),
) -> User:
	return user


async def get_current_superuser(
	user: User = Depends(fastapi_users.current_user(active=True, superuser=True)),
) -> User:
	return user
