from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.auth import get_current_active_user
from app.dependencies import get_fillings_service
from app.dtos.filling_dto import FillingDTO
from app.schemas import UserRead
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
	filling.license_plate_number = filling.license_plate_number.strip().upper()
	filling.type = filling.type.strip()

	await service.save_history_record(filling=filling, user=user)

	return JSONResponse(
		status_code=status.HTTP_200_OK,
		content={"message": "Filling stored successfully"},
	)