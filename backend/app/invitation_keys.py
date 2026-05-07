import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import InvitationKey
from app.repositories.invitation_key_repository import InvitationKeyRepository

logger = logging.getLogger("app.invitation_keys")


async def sync_invitation_keys(session: AsyncSession) -> None:
	repo = InvitationKeyRepository(session)
	env_keys = set(settings.invitation_keys)

	db_keys = await repo.get_all()
	db_keys_set = {k.key for k in db_keys}

	keys_to_delete = db_keys_set - env_keys
	if keys_to_delete:
		logger.info("Removing %d expired invitation key(s) from DB", len(keys_to_delete))
		users_with_deleted_keys = await repo.get_users_by_invitation_keys(keys_to_delete)
		for user in users_with_deleted_keys:
			user.invitation_key_id = None

		await repo.delete_by_keys(keys_to_delete)

	keys_to_add = env_keys - db_keys_set
	if keys_to_add:
		logger.info("Adding %d new invitation key(s) to DB", len(keys_to_add))
	for key in keys_to_add:
		repo.add(InvitationKey(key=key))

	await repo.commit()
