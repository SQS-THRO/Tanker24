from io import StringIO
import csv


from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from starlette.responses import StreamingResponse

from app.auth import get_current_active_user
from app.database import get_db
from app.models import HistoryRecord, Car
from app.schemas.user import UserRead
from app.services.export_data_service import ExportDataService
from app.dependencies import get_flat_export_data_service, get_nested_export_data_service

router = APIRouter(prefix="/export", tags=["export"])


@router.get(
	"/json",
	status_code=status.HTTP_200_OK,
	summary="Get the user data as json",
	description="Returns the user data of the authenticated user as a json string.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def get_user_data_as_json(
    user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[ExportDataService, Depends(get_nested_export_data_service)],
) -> JSONResponse:
	result = await service.get_user_data(user.id)
	return JSONResponse(content=result, headers={"Content-Disposition": "attachment; filename=user_data.json"})


# Returns a csv file containing the user data. As csv files can't contain nested data the car_id is part of each row
@router.get(
	"/csv",
	status_code=status.HTTP_200_OK,
	summary="Get the user data as semicolon separated csv file.",
	description="Returns the user data of the authenticated user as a semicolon separated csv.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def get_user_data_as_csv(
	user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[ExportDataService, Depends(get_flat_export_data_service)],

) -> StreamingResponse:
	result = await service.get_user_data(user.id)

	# Fill an StringIO pseudo file with the data
	output = StringIO()
	writer = csv.DictWriter(
		output,
		delimiter=";",
		fieldnames=[
			"id",
			"car_id",
			"car_type",
			"license_plate_number",
			"created_at",
			"mileage",
			"price_per_litre",
			"litres",
			"total_price",
			"fuel_type",
		],
	)
	writer.writeheader()
	writer.writerows(result)

	output.seek(0)

	return StreamingResponse(
		iter([output.getvalue()]),
		media_type="text/csv",
		headers={"Content-Disposition": "attachment; filename=car_history_data.csv"},
	)
