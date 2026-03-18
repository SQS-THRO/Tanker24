from typing import List

from app.dtos.gas_station_dtos import GasStation, OpeningTime

import httpx


""" 
The actual GasStation Service which communicates with the tankerkoenig api.
It offers function for using an area search and getting data for a specific station.
"""
class GasStationService:
    # Static base url
    BASE_URL = "https://creativecommons.tankerkoenig.de/json/"

    def __init__(self, api_key: str = "00000000-0000-0000-0000-000000000002"):
        self.api_key = api_key

    def get_gas_station_by_id(self, id: str):
        endpoint_url = "detail.php"
        # Required parameters for the api
        params = {
            "id": id,
            "apikey": self.api_key
        }

        response = httpx.get(self.BASE_URL+endpoint_url, params=params, timeout=10.0)
        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError("Tankerkoenig API was unable to return the data for a specific station. The request was bad.")

        station = data.get("station")

        # prepare opening times as they are an array in the original received JSON
        opening_times: List[OpeningTime] = []
        for opening_time in station.get("openingTimes", []):
            opening_times.append(
                OpeningTime(
                    text=opening_time.get("text"),
                    start=opening_time.get("start"),
                    end=opening_time.get("end"),
                )
            )

        result = GasStation(
            id=station.get("id"),
            name=station.get("name"),
            brand=station.get("brand"),
            street=station.get("street"),
            house_number=station.get("houseNumber"),
            post_code=station.get("postCode"),
            place=station.get("place"),
            latitude=station.get("lat"),
            longitude=station.get("lng"),
            distance=station.get("dist"),
            is_open=station.get("isOpen"),
            diesel=station.get("diesel"),
            e5=station.get("e5"),
            e10=station.get("e10"),
            whole_day=station.get("wholeDay"),
            overrides=station.get("overrides"),
            opening_times=opening_times
        )


        return result

    # It is possible to set the desired fuel type in the api request for more specific filtering. Use the enum FuelType for applying this filter
    def get_gas_stations(
        self,
        latitude: float,
        longitude: float,
        radius: float
    ) -> List[GasStation]:
        endpoint_url = "list.php"

        # Required parameters for the api
        params = {
            "lat": latitude,
            "lng": longitude,
            "rad": radius,
            "sort": "dist",
            "type": "all",
            "apikey": self.api_key,
        }

        response = httpx.get(self.BASE_URL+endpoint_url, params=params, timeout=10.0)
        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError("Tankerkoenig API returned an error. The request was bad.")

        # prepare a list of stations to return.
        result: List[GasStation] = []

        # Loop over the received array of gas stations
        for station in data.get("stations", []):

            result.append(
                GasStation(
                    id=station.get("id"),
                    name=station.get("name"),
                    brand=station.get("brand"),
                    street=station.get("street"),
                    house_number=station.get("houseNumber"),
                    post_code=station.get("postCode"),
                    place=station.get("place"),
                    latitude=station.get("lat"),
                    longitude=station.get("lng"),
                    distance=station.get("dist"),
                    is_open=station.get("isOpen"),
                    diesel=station.get("diesel"),
                    e5=station.get("e5"),
                    e10=station.get("e10"),
                )
            )

        return result