from app.schemas.station import Station as StationSchema

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class FuelType(str, Enum):
	diesel = "diesel"
	e5 = "e5"
	e10 = "e10"
	all = "all"


class OpeningTime:
	def __init__(self, text: str, start: str, end: str):
		self.text = text
		self.start = datetime.strptime(start, "%H:%M:%S").time()
		self.end = datetime.strptime(end, "%H:%M:%S").time()


# Map the data from the received JSON to a GasStation object
@dataclass
class GasStation:
	"""Class for handling gas station data."""

	id: str
	name: str
	brand: str
	street: str
	house_number: str
	post_code: int
	place: str
	latitude: float
	longitude: float
	is_open: bool
	# prices are optional because not all stations offer all 3 types of gas
	diesel: Optional[float]
	e5: Optional[float]
	e10: Optional[float]
	whole_day: Optional[bool] = None
	overrides: Optional[List[str]] = None
	opening_times: Optional[List[OpeningTime]] = None
	distance: Optional[float] = None


# Map the station schema to a DTO to send it to the frontend
class GasStationInternalDTO(BaseModel):
	"""Class for handling gas station data."""

	id: int
	tankerkoenig_id: str
	name: str
	brand: str
	street: Optional[str] = None
	house_number: Optional[str] = None
	post_code: Optional[int] = None
	place: Optional[str] = None
	latitude: float
	longitude: float
	is_open: bool
	# prices are optional because not all stations offer all 3 types of gas
	diesel: Optional[float]
	e5: Optional[float]
	e10: Optional[float]
	distance: Optional[float] = None
	cached_at: Optional[datetime] = None
	cache_lat: Optional[float] = None
	cache_lon: Optional[float] = None
	cache_radius: Optional[float] = None

	@classmethod
	def from_schema(cls, station: StationSchema) -> "GasStationInternalDTO":
		return cls(
			id=station.id,
			tankerkoenig_id=station.tankerkoenig_id,
			name=station.name,
			brand=station.brand,
			street=station.street,
			house_number=station.house_number,
			post_code=station.post_code,
			place=station.place,
			latitude=station.latitude,
			longitude=station.longitude,
			is_open=station.is_open,
			distance=getattr(station, "distance", None),
			diesel=station.diesel,
			e5=station.e5,
			e10=station.e10,
			cached_at=getattr(station, "cached_at", None),
			cache_lat=getattr(station, "cache_lat", None),
			cache_lon=getattr(station, "cache_lon", None),
			cache_radius=getattr(station, "cache_radius", None),
		)
