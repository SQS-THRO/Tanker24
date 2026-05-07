from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user_with_request_state
from app.limiter import limiter
from app.models import Station
from app.repositories.station_repository import StationRepository
from app.repositories.tankerkoenig_station_repository import TankerkoenigStationRepository
from app.schemas.station import Station as StationSchema
from app.schemas.station import StationCreate, StationUpdate, TankerkoenigStation
from app.schemas.user import UserRead
from app.services.nearby_stations_service import NearbyStationsService
from app.services.station_service import StationService

router = APIRouter(prefix="/stations", tags=["stations"])

STATION_NOT_FOUND = "Station not found"


def _validate_station(station: Station | StationSchema) -> StationSchema:
	try:
		return StationSchema.model_validate(station)
	except ValidationError:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
			detail="Invalid station data",
		)


@router.get(
	"/",
	summary="List all stations",
	description="Retrieve a list of all gas stations owned by the authenticated user.",
)
async def list_stations(
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> list[StationSchema]:
	service = StationService(StationRepository(db))
	stations = await service.get_stations_by_owner(user.id)
	return [_validate_station(s) for s in stations]


@router.post(
	"/",
	status_code=status.HTTP_201_CREATED,
	summary="Create a new station",
	description="Create a new gas station owned by the authenticated user.",
)
async def create_station(
	station: StationCreate,
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> StationSchema:
	service = StationService(StationRepository(db))
	db_station = await service.create_station(station, user.id)
	return _validate_station(db_station)


@router.get(
	"/nearby",
	summary="Get nearby gas stations",
	description="Fetch gas stations around a given latitude and longitude. Uses cached data when available and not expired.",
	responses={
		status.HTTP_400_BAD_REQUEST: {
			"description": "Invalid latitude or longitude parameters",
			"content": {"application/json": {"example": {"detail": "Latitude must be between -90 and 90"}}},
		},
		status.HTTP_429_TOO_MANY_REQUESTS: {
			"description": "Rate limit exceeded",
			"content": {"application/json": {"example": {"detail": "Rate limit exceeded"}}},
		},
	},
)
@limiter.limit(settings.nearby_stations_rate_limit)
async def get_nearby_stations(
	request: Request,
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_user_with_request_state)],
	latitude: Annotated[float, Query(ge=-90, le=90, description="Latitude coordinate (-90 to 90)")],
	longitude: Annotated[float, Query(ge=-180, le=180, description="Longitude coordinate (-180 to 180)")],
) -> list[TankerkoenigStation]:
	try:
		service = NearbyStationsService(TankerkoenigStationRepository(db))
		return await service.get_nearby_stations(latitude, longitude)
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
	"/{station_id}",
	summary="Get a station by ID",
	description="Retrieve details of a specific gas station by its ID. Only accessible by the station owner.",
	responses={404: {"description": STATION_NOT_FOUND}},
)
async def get_station(
	station_id: int,
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> StationSchema:
	service = StationService(StationRepository(db))
	station = await service.get_station_by_id_and_owner(station_id, user.id)
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)
	return _validate_station(station)


@router.patch(
	"/{station_id}",
	summary="Update a station",
	description="Update an existing gas station. Only station attributes provided in the request body will be modified (partial update).",
	responses={404: {"description": STATION_NOT_FOUND}},
)
async def update_station(
	station_id: int,
	station_update: StationUpdate,
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> StationSchema:
	service = StationService(StationRepository(db))
	station = await service.get_station_by_id_and_owner(station_id, user.id)
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)

	station = await service.update_station(station, station_update)
	return _validate_station(station)


@router.delete(
	"/{station_id}",
	status_code=status.HTTP_204_NO_CONTENT,
	summary="Delete a station",
	description="Delete a gas station by its ID. This action is permanent and cannot be undone. Only accessible by the station owner.",
	responses={404: {"description": STATION_NOT_FOUND}},
)
async def delete_station(
	station_id: int,
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> None:
	service = StationService(StationRepository(db))
	station = await service.get_station_by_id_and_owner(station_id, user.id)
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)

	await service.delete_station(station)
