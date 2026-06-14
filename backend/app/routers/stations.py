from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user_with_request_state
from app.dtos.gas_station_dtos import GasStationInternalDTO
from app.limiter import limiter
from app.repositories.station_repository import StationRepository
from app.schemas.station import Station as StationSchema
from app.schemas.user import UserRead
from app.services.nearby_stations_service import NearbyStationsService

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get(
	"/",
	summary="List all stations",
	description="Retrieve a list of all cached gas stations from the Tankerkoenig API.",
)
async def list_stations(
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
) -> list[GasStationInternalDTO]:
    repository = StationRepository(db)
    stations = await repository.get_all_stations()

    return [
        GasStationInternalDTO.from_schema(StationSchema.model_validate(station))
        for station in stations
    ]


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
) -> list[GasStationInternalDTO]:
    try:
        service = NearbyStationsService(StationRepository(db))
        stations = await service.get_nearby_stations(latitude, longitude)

        return [
            GasStationInternalDTO.from_schema(StationSchema.model_validate(station))
            for station in stations
        ]

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
