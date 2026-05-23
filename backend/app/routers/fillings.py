from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse

from app.auth import get_current_active_user
from app.dependencies import get_fillings_service
from app.dtos.filling_dto import FillingDTO
from app.dtos.gas_station_dtos import FuelType
from app.schemas.user import UserRead
from app.services.fillings_service import FillingsService

router = APIRouter(prefix="/fillings", tags=["fillings"])


@router.post(
	"/create",
	status_code=status.HTTP_200_OK,
	summary="Create anew filling in the database for the authenticated user",
	description="Stores the received filling data for the user in the database.",
	responses={503: {"description": "Database temporarily unavailable."}},
)
async def post_filling_data(
	filling: FillingDTO,
	user: Annotated[UserRead, Depends(get_current_active_user)],
	service: Annotated[FillingsService, Depends(get_fillings_service)],
) -> JSONResponse:
	#Input sanitization
	filling.license_plate_number = filling.license_plate_number.strip().upper()

	fuel_type = filling.fuel_type.lower()

	if fuel_type not in FuelType.__members__:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail=f"Fuel type '{fuel_type}' not found",
		)

	await service.save_history_record(filling=filling, user=user)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={"message": "Filling stored successfully"},
	)
