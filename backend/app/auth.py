import re
from typing import Any, Annotated

from fastapi import Depends, Request
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
	AuthenticationBackend,
	BearerTransport,
	JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.manager import BaseUserManager
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_users import schemas
from app.config import settings
from app.database import get_db
from app.models import InvitationKey, User
from app.schemas.user import UserCreate, UserRead


class CustomUserManager(BaseUserManager[User, int]):
	user_read_model = UserRead
	user_create_model = UserCreate

	async def validate_password(
		self,
		password: str,
		user: Any = None,
	) -> None:
		if len(password) < 8:
			raise InvalidPasswordException(reason="Password must be at least 8 characters")
		if not re.search(r"[A-Z]", password):
			raise InvalidPasswordException(reason="Password must contain an uppercase letter")
		if not re.search(r"[a-z]", password):
			raise InvalidPasswordException(reason="Password must contain a lowercase letter")
		if not re.search(r"[0-9]", password):
			raise InvalidPasswordException(reason="Password must contain a number")
		if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
			raise InvalidPasswordException(reason="Password must contain a special character")

	async def create(
		self,
		user_create: schemas.UC,
		safe: bool = False,
		request: Request | None = None,
	) -> User:
		await self.validate_password(user_create.password, user_create)

		existing_user = await self.user_db.get_by_email(user_create.email)
		if existing_user:
			raise UserAlreadyExists()

		user_dict = user_create.create_update_dict()
		password = user_dict.pop("password")
		invitation_key_str = user_dict.pop("invitation_key", "")

		if settings.invitation_keys:
			result = await self.user_db.session.execute(  # type: ignore[attr-defined]
				select(InvitationKey).where(InvitationKey.key == invitation_key_str)
			)
			invitation_key = result.scalar_one_or_none()
			if not invitation_key:
				raise InvalidPasswordException(reason="Invalid invitation key")
			user_dict["invitation_key_id"] = invitation_key.id

		hashed_password = self.password_helper.hash(password)
		db_obj = User(**user_dict, hashed_password=hashed_password)
		self.user_db.session.add(db_obj)  # type: ignore[attr-defined]
		await self.user_db.session.commit()  # type: ignore[attr-defined]

		await self.on_after_register(db_obj, request)

		return db_obj

	async def on_after_register(self, user: User, request: Request | None = None) -> None:
		"""
		Hook called after a user registers.

		Intentionally empty: no additional actions (e.g., sending welcome emails,
		activating accounts, or triggering workflows) currently.
		"""
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


def get_jwt_strategy() -> JWTStrategy[User, int]:
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


def get_current_user(
	user: Annotated[User, Depends(fastapi_users.current_user(active=True))],
) -> UserRead:
	return UserRead.model_validate(user)


def get_current_active_user(
	user: Annotated[User, Depends(fastapi_users.current_user(active=True))],
) -> UserRead:
	return UserRead.model_validate(user)


def get_current_superuser(
	user: Annotated[User, Depends(fastapi_users.current_user(active=True, superuser=True))],
) -> UserRead:
	return UserRead.model_validate(user)
