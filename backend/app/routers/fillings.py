import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.auth import get_current_active_user
from app.dependencies import get_fillings_service
from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.exceptions.exceptions import FillingNotFoundException
from app.schemas.user import UserRead
from app.services.fillings_service import FillingsService

logger = logging.getLogger("app.routers.fillings")

router = APIRouter(prefix="/fillings", tags=["fillings"])


@router.post(
	"/create",
	status_code=status.HTTP_200_OK,
	summary="Create a new filling in the database for the authenticated user",
	description="Stores the received filling data for the user in the database.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def post_filling_data(
	filling: FillingDTO,
	user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[FillingsService, Depends(get_fillings_service)],
) -> JSONResponse:

	# Input sanitization
	filling.license_plate_number = filling.license_plate_number.strip().upper()

	fuel_type = filling.fuel_type.lower()

	if fuel_type not in FuelType.__members__:
		logging.info("Endpoint post_filling_data detected a bad request!")
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Fuel type '{fuel_type}' not found",
		)

	await service.save_history_record(filling=filling, user=user)

	logger.info(f"Created filling for user {user.email}")
	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={"message": "Filling stored successfully"},
	)


@router.delete(
	"/delete",
	status_code=status.HTTP_200_OK,
	summary="Deletes filling data by ID for authenticated users.",
	description="Deletes filling data by ID for authenticated users.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def delete_filling_data(
	filling_id: Annotated[int, Query(gt=0)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[FillingsService, Depends(get_fillings_service)],
) -> JSONResponse:
	try:
		await service.delete_history_record(
			history_record_id=filling_id,
			user=user,
		)
		logger.info(f"Deleted filling {filling_id} for user {user.email}")
	except FillingNotFoundException as exc:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=str(exc),
		) from exc

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={"message": "Filling deleted successfully"},
	)


@router.get(
	path="",
	status_code=status.HTTP_200_OK,
	summary="Returns the history records for the authenticated user.",
	description="Returns the history records for the authenticated user.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def get_filling_data_from_user(
	user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[FillingsService, Depends(get_fillings_service)],
) -> JSONResponse:

	result = await service.get_filling_dto_for_user(
		user=user,
	)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content=jsonable_encoder(result),
	)
