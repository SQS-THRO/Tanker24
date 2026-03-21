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


def _validate_station(station: Station | StationSchema) -> StationSchema:
	try:
		return StationSchema.model_validate(station)
	except ValidationError:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail="Invalid station data",
		)


@router.get("/", response_model=list[StationSchema])
async def list_stations(
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> list[StationSchema]:
	result = await db.execute(select(Station).where(Station.owner_id == user.id))
	stations = result.scalars().all()
	return [_validate_station(s) for s in stations]


@router.post("/", response_model=StationSchema, status_code=status.HTTP_201_CREATED)
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


@router.get("/{station_id}", response_model=StationSchema)
async def get_station(
	station_id: int,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> StationSchema:
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
	return _validate_station(station)


@router.patch("/{station_id}", response_model=StationSchema)
async def update_station(
	station_id: int,
	station_update: StationUpdate,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> StationSchema:
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

	update_data = station_update.model_dump(exclude_unset=True)
	for key, value in update_data.stations():
		setattr(station, key, value)

	await db.commit()
	await db.refresh(station)
	return _validate_station(station)


@router.delete("/{station_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_station(
	station_id: int,
	db: AsyncSession = Depends(get_db),
	user: User = Depends(get_current_active_user),
) -> None:
	result = await db.execute(select(Station).where(Station.id == station_id, Station.owner_id == user.id))
	station = result.scalar_one_or_none()
	if not station:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")

	await db.delete(station)
	await db.commit()
