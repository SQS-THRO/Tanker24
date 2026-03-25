import pytest


@pytest.mark.asyncio
class TestHealthEndpoints:
    async def test_health_check(self, async_client):
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "Tanker24 Backend"
        assert data["version"] == "1.0.0"

    async def test_root_endpoint(self, async_client):
        response = await async_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Tanker24 Backend v1.0.0"
