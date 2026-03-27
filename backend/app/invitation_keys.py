from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import InvitationKey, User


async def sync_invitation_keys(session: AsyncSession) -> None:
	env_keys = set(settings.invitation_keys)

	result = await session.execute(select(InvitationKey))
	db_keys = result.scalars().all()
	db_keys_set = {k.key for k in db_keys}

	keys_to_delete = db_keys_set - env_keys
	if keys_to_delete:
		result = await session.execute(
			select(User).join(InvitationKey).where(InvitationKey.key.in_(keys_to_delete))
		)
		users_with_deleted_keys: list[User] = result.scalars().all()  # type: ignore[assignment]
		for user in users_with_deleted_keys:
			user.invitation_key_id = None

		await session.execute(
			delete(InvitationKey).where(InvitationKey.key.in_(keys_to_delete))
		)

	keys_to_add = env_keys - db_keys_set
	for key in keys_to_add:
		session.add(InvitationKey(key=key))

	await session.commit()
