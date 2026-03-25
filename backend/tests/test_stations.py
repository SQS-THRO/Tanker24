import pytest


@pytest.mark.asyncio
class TestStationList:
	async def test_list_stations_authenticated_empty(self, authenticated_client):
		response = await authenticated_client.get("/stations/")

		assert response.status_code == 200
		assert response.json() == []

	async def test_list_stations_authenticated_with_stations(self, authenticated_client, owned_station):
		response = await authenticated_client.get("/stations/")

		assert response.status_code == 200
		data = response.json()
		assert len(data) == 1
		assert data[0]["name"] == owned_station.name
		assert data[0]["description"] == owned_station.description
		assert data[0]["owner_id"] == owned_station.owner_id

	async def test_list_stations_unauthenticated(self, async_client):
		response = await async_client.get("/stations/")

		assert response.status_code == 401

	async def test_list_stations_only_shows_own_stations(self, authenticated_client, owned_station, other_user_station):
		response = await authenticated_client.get("/stations/")

		assert response.status_code == 200
		data = response.json()
		assert len(data) == 1
		assert data[0]["id"] == owned_station.id
		assert data[0]["name"] != other_user_station.name


@pytest.mark.asyncio
class TestStationCreate:
	async def test_create_station_success(self, authenticated_client, station_data):
		response = await authenticated_client.post("/stations/", json=station_data)

		assert response.status_code == 201
		data = response.json()
		assert data["name"] == station_data["name"]
		assert data["description"] == station_data["description"]
		assert "id" in data
		assert "owner_id" in data

	async def test_create_station_without_description(self, authenticated_client):
		response = await authenticated_client.post("/stations/", json={"name": "Station Without Desc"})

		assert response.status_code == 201
		data = response.json()
		assert data["name"] == "Station Without Desc"
		assert data["description"] is None

	async def test_create_station_unauthenticated(self, async_client, station_data):
		response = await async_client.post("/stations/", json=station_data)

		assert response.status_code == 401

	async def test_create_station_missing_name(self, authenticated_client):
		response = await authenticated_client.post("/stations/", json={"description": "No name"})

		assert response.status_code == 422


@pytest.mark.asyncio
class TestStationGet:
	async def test_get_station_success(self, authenticated_client, owned_station):
		response = await authenticated_client.get(f"/stations/{owned_station.id}")

		assert response.status_code == 200
		data = response.json()
		assert data["id"] == owned_station.id
		assert data["name"] == owned_station.name
		assert data["description"] == owned_station.description

	async def test_get_station_not_found(self, authenticated_client):
		response = await authenticated_client.get("/stations/99999")

		assert response.status_code == 404
		assert response.json()["detail"] == "Station not found"

	async def test_get_other_user_station(self, authenticated_client, other_user_station):
		response = await authenticated_client.get(f"/stations/{other_user_station.id}")

		assert response.status_code == 404

	async def test_get_station_unauthenticated(self, async_client, owned_station):
		response = await async_client.get(f"/stations/{owned_station.id}")

		assert response.status_code == 401


@pytest.mark.asyncio
class TestStationUpdate:
	async def test_update_station_not_found(self, authenticated_client):
		response = await authenticated_client.patch("/stations/99999", json={"name": "Updated Name"})

		assert response.status_code == 404
		assert response.json()["detail"] == "Station not found"

	async def test_update_other_user_station(self, authenticated_client, other_user_station):
		response = await authenticated_client.patch(f"/stations/{other_user_station.id}", json={"name": "Hacked Name"})

		assert response.status_code == 404

	async def test_update_station_unauthenticated(self, async_client, owned_station):
		response = await async_client.patch(f"/stations/{owned_station.id}", json={"name": "Updated"})

		assert response.status_code == 401


@pytest.mark.asyncio
class TestStationDelete:
	async def test_delete_station_success(self, authenticated_client, owned_station):
		response = await authenticated_client.delete(f"/stations/{owned_station.id}")

		assert response.status_code == 204

		get_response = await authenticated_client.get(f"/stations/{owned_station.id}")
		assert get_response.status_code == 404

	async def test_delete_station_not_found(self, authenticated_client):
		response = await authenticated_client.delete("/stations/99999")

		assert response.status_code == 404
		assert response.json()["detail"] == "Station not found"

	async def test_delete_other_user_station(self, authenticated_client, other_user_station):
		response = await authenticated_client.delete(f"/stations/{other_user_station.id}")

		assert response.status_code == 404

	async def test_delete_station_unauthenticated(self, async_client, owned_station):
		response = await async_client.delete(f"/stations/{owned_station.id}")

		assert response.status_code == 401
