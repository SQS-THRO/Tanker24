# dependencies.py

from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.database import get_db
from app.services.export_data_service import ExportDataService, FlatExportDataService, NestedExportDataService


def get_nested_export_data_service(
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ExportDataService:
	return NestedExportDataService(db)


def get_flat_export_data_service(
	db: Annotated[AsyncSession, Depends(get_db)],
) -> ExportDataService:
	return FlatExportDataService(db)


async def get_current_user_with_request_state(
	request: Request,
	user: Annotated[object, Depends(get_current_active_user)],
) -> object:
	"""Get current user and store it in request.state for rate limiter access."""
	request.state.user = user
	return user
