from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InvitationKey, User


class InvitationKeyRepository:
	def __init__(self, db: AsyncSession) -> None:
		self.db = db

	async def get_all(self) -> list[InvitationKey]:
		result = await self.db.execute(select(InvitationKey))
		return list(result.scalars().all())

	async def find_by_key(self, key: str) -> InvitationKey | None:
		result = await self.db.execute(select(InvitationKey).where(InvitationKey.key == key))
		return result.scalar_one_or_none()

	async def delete_by_keys(self, keys: set[str]) -> None:
		if keys:
			await self.db.execute(delete(InvitationKey).where(InvitationKey.key.in_(keys)))

	async def add(self, invitation_key: InvitationKey) -> None:
		self.db.add(invitation_key)

	async def commit(self) -> None:
		await self.db.commit()

	async def get_users_by_invitation_keys(self, keys: set[str]) -> list[User]:
		result = await self.db.execute(select(User).join(InvitationKey).where(InvitationKey.key.in_(keys)))
		return list(result.scalars().all())
