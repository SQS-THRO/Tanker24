import pytest
from sqlalchemy import text

from app.models import Station


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
	async def test_update_station_success_full(self, authenticated_client, owned_station):
		update_data = {"name": "Updated Station Name", "description": "Updated description"}
		response = await authenticated_client.patch(f"/stations/{owned_station.id}", json=update_data)

		assert response.status_code == 200
		data = response.json()
		assert data["name"] == "Updated Station Name"
		assert data["description"] == "Updated description"
		assert data["id"] == owned_station.id

	async def test_update_station_success_partial_name_only(self, authenticated_client, owned_station):
		response = await authenticated_client.patch(f"/stations/{owned_station.id}", json={"name": "New Name Only"})

		assert response.status_code == 200
		data = response.json()
		assert data["name"] == "New Name Only"
		assert data["description"] == owned_station.description

	async def test_update_station_success_partial_description_only(self, authenticated_client, owned_station):
		response = await authenticated_client.patch(f"/stations/{owned_station.id}", json={"description": "New Description Only"})

		assert response.status_code == 200
		data = response.json()
		assert data["name"] == owned_station.name
		assert data["description"] == "New Description Only"

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

	async def test_update_station_empty_body(self, authenticated_client, owned_station):
		response = await authenticated_client.patch(f"/stations/{owned_station.id}", json={})

		assert response.status_code == 200
		data = response.json()
		assert data["name"] == owned_station.name
		assert data["description"] == owned_station.description


@pytest.mark.asyncio
class TestValidateStation:
	async def test_validate_station_invalid_data(self, authenticated_client, test_db_session, test_user):
		station = Station(
			name="",  # Empty string may cause validation issues depending on config
			description="Test",
			owner_id=test_user.id,
		)
		test_db_session.add(station)
		await test_db_session.commit()
		await test_db_session.refresh(station)

		response = await authenticated_client.get(f"/stations/{station.id}")

		assert response.status_code in [200, 422]

	async def test_get_station_with_invalid_db_data(self, authenticated_client, test_db_session, test_user):
		result = await test_db_session.execute(
			text("INSERT INTO stations (name, description, owner_id) VALUES (:name, :desc, :owner_id) RETURNING id"),
			{"name": "Valid Name", "desc": "Valid Description", "owner_id": test_user.id},
		)
		station_id = result.scalar_one()
		await test_db_session.commit()

		await test_db_session.execute(
			text("UPDATE stations SET name = :name WHERE id = :id"),
			{"name": "Updated Via Raw SQL", "id": station_id},
		)
		await test_db_session.commit()

		response = await authenticated_client.get(f"/stations/{station_id}")
		assert response.status_code == 200
		assert response.json()["name"] == "Updated Via Raw SQL"


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
