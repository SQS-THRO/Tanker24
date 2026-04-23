from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Station
from app.schemas.station import Station as StationSchema
from app.schemas.station import StationCreate, StationUpdate, TankerkoenigStation
from app.schemas.user import UserRead
from app.services.nearby_stations_service import NearbyStationsService

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
	result = await db.execute(select(Station).where(Station.owner_id == user.id))
	stations = result.scalars().all()
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
	db_station = Station(**station.model_dump(), owner_id=user.id)
	db.add(db_station)
	await db.commit()
	await db.refresh(db_station)
	return _validate_station(db_station)


@router.get(
	"/nearby",
	summary="Get nearby gas stations",
	description="Fetch gas stations around a given latitude and longitude. Uses cached data when available and not expired.",
	responses={
		400: {"description": "Invalid latitude or longitude parameters"},
	},
)
async def get_nearby_stations(
	db: Annotated[AsyncSession, Depends(get_db)],
	user: Annotated[UserRead, Depends(get_current_active_user)],
	latitude: float = Query(..., description="Latitude coordinate (-90 to 90)"),
	longitude: float = Query(..., description="Longitude coordinate (-180 to 180)"),
) -> list[TankerkoenigStation]:
	try:
		service = NearbyStationsService(db)
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
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
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
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)

	update_data = station_update.model_dump(exclude_unset=True)
	for key, value in update_data.items():
		setattr(station, key, value)

	await db.commit()
	await db.refresh(station)
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
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)

	await db.delete(station)
	await db.commit()
