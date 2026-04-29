# dependencies.py

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

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