from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_active_user
from app.database import get_db
from app.models import Station, User
from app.schemas.station import Station as StationSchema
from app.schemas.station import StationCreate, StationUpdate

router = APIRouter(prefix="/stations", tags=["stations"])

STATION_NOT_FOUND = "Station not found"


def _validate_station(station: Station | StationSchema) -> StationSchema:
	try:
		return StationSchema.model_validate(station)
	except ValidationError:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail="Invalid station data",
		)


@router.get(
	"/",
	response_model=list[StationSchema],
	summary="List all stations",
	description="Retrieve a list of all gas stations owned by the authenticated user.",
)
async def list_stations(
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> list[StationSchema]:
	result = await db.execute(select(Station).where(Station.owner_id == user.id))
	stations = result.scalars().all()
	return [_validate_station(s) for s in stations]


@router.post(
	"/",
	response_model=StationSchema,
	status_code=status.HTTP_201_CREATED,
	summary="Create a new station",
	description="Create a new gas station owned by the authenticated user.",
)
async def create_station(
	station: StationCreate,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> StationSchema:
	db_station = Station(**station.model_dump(), owner_id=user.id)
	db.add(db_station)
	await db.commit()
	await db.refresh(db_station)
	return _validate_station(db_station)


@router.get(
	"/{station_id}",
	response_model=StationSchema,
	summary="Get a station by ID",
	description="Retrieve details of a specific gas station by its ID. Only accessible by the station owner.",
	responses={404: {"description": STATION_NOT_FOUND}},
)
async def get_station(
	station_id: int,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> StationSchema:
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)
	return _validate_station(station)


@router.patch(
	"/{station_id}",
	response_model=StationSchema,
	summary="Update a station",
	description="Update an existing gas station. Only station attributes provided in the request body will be modified (partial update).",
	responses={404: {"description": STATION_NOT_FOUND}},
)
async def update_station(
	station_id: int,
	station_update: StationUpdate,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
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
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> None:
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=STATION_NOT_FOUND)

	await db.delete(station)
	await db.commit()
