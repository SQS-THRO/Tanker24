import pytest
from app.services.gas_station_service import GasStationService, FuelType

def test_get_stations():
    service = GasStationService()
    #https://creativecommons.tankerkoenig.de/json/list.php?lat=52.521&lng=13.438&rad=1.5&sort=dist&type=all&apikey=00000000-0000-0000-0000-000000000002
    result = service.get_gas_stations(latitude=52.521, longitude= 13.438, radius = 5)

    assert type(result) == list