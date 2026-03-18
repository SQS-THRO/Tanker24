import pytest
from app.services.gas_station_service import GasStationService
from app.dtos.gas_station_dtos import GasStation, OpeningTime, FuelType

def test_get_stations():
    service = GasStationService()
    result = service.get_gas_stations(latitude=52.521, longitude= 13.438, radius = 5)

    assert isinstance(result,list)