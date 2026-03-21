from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


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
	opening_times: Optional[OpeningTime] = None
	distance: Optional[float] = None
