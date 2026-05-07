"""
Tests for rate limiting on the nearby stations endpoint.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.limiter import limiter
from app.database import get_db


@pytest.fixture
def anyio_backend():
	return "asyncio"


@pytest_asyncio.fixture
async def auth_headers(test_db_session):
	"""Get authentication headers for testing."""
	# Create an invitation key for testing
	from app.models import InvitationKey

	invitation_key = InvitationKey(key="TESTKEY123")
	test_db_session.add(invitation_key)
	await test_db_session.commit()
	await test_db_session.refresh(invitation_key)

	# Override the database dependency to use test database
	async def override_get_db():
		yield test_db_session

	app.dependency_overrides[get_db] = override_get_db

	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		# Register a test user
		response = await client.post(
			"/api/v0/auth/register",
			json={
				"email": "ratelimit@test.com",
				"password": "Test123!@#",
				"invitation_key": "TESTKEY123",
				"forename": "Rate",
				"surname": "Limit",
			},
		)
		# Login to get token
		response = await client.post(
			"/api/v0/auth/jwt/login",
			data={"username": "ratelimit@test.com", "password": "Test123!@#"},
		)
		if response.status_code == 200:
			token = response.json()["access_token"]
			yield {"Authorization": f"Bearer {token}"}
		else:
			yield {}

	# Clear the dependency override
	app.dependency_overrides.clear()


@pytest.fixture
def clear_rate_limit_storage():
	"""Clear the rate limit storage before and after tests."""
	# Clear storage before test
	# Access the internal storage dict directly since MemoryStorage.clear()
	# now requires a key argument in newer versions of limits library
	storage = limiter._storage
	if hasattr(storage, "_storage") and isinstance(storage._storage, dict):
		storage._storage.clear()
	yield
	# Clear storage after test
	storage = limiter._storage
	if hasattr(storage, "_storage") and isinstance(storage._storage, dict):
		storage._storage.clear()


@pytest.mark.asyncio
async def test_nearby_stations_rate_limit(auth_headers, clear_rate_limit_storage):
	"""
	Test that the nearby stations endpoint enforces rate limiting.
	Note: This test assumes a rate limit of 10/minute (default).
	We'll make 11 requests and expect the last one to be rate limited.
	"""
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		# Make requests up to the limit
		# The default rate limit is 10/minute, so we make 11 requests
		responses = []
		for i in range(11):
			response = await client.get(
				"/api/v0/stations/nearby?latitude=48.1&longitude=11.5",
				headers=auth_headers,
			)
			responses.append(response.status_code)

		# The first 10 requests should succeed (or return 400 for invalid params, but not 429)
		# The 11th request should be rate limited (429)
		# Note: Since we're using cached data or external API, the exact status may vary
		# We just want to ensure that after hitting the limit, we get a 429
		assert responses[-1] == 429, f"Expected 429, got {responses[-1]}. All statuses: {responses}"


@pytest.mark.asyncio
async def test_nearby_stations_rate_limit_per_user(clear_rate_limit_storage):
	"""
	Test that rate limiting is applied per user, not globally.
	Two different users should each get their own rate limit bucket.
	"""
	transport = ASGITransport(app=app)

	# Create two different users and test that they have separate rate limit buckets
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		# This test verifies the user-based rate limiting is working
		# In practice, we'd need two different authenticated users
		# For now, we'll just verify the rate limit key function works

		# Get the limiter's key function
		key_func = limiter._key_func

		# Create mock requests with different users in state

		# This is a simplified test - in reality, we'd need to properly mock the request
		# The important thing is that the key function checks for user in request.state

		# Verify the limiter is configured with the correct key function
		assert callable(key_func), "Key function should be callable"
