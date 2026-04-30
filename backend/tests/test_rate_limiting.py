"""
Tests for per-user rate limiting on the /stations/nearby endpoint.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from httpx import AsyncClient

from app.models import User
from app.services.rate_limiter import user_rate_limiter

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def reset_rate_limiter():
	"""Clear rate limiter state before each test and restore original values."""
	original_states = user_rate_limiter._user_states.copy()
	original_last_cleanup = user_rate_limiter._last_cleanup
	original_rate_limit = user_rate_limiter.rate_limit

	user_rate_limiter._user_states.clear()
	user_rate_limiter._last_cleanup = time.monotonic()

	yield

	# Restore original values to avoid cross-test contamination
	user_rate_limiter._user_states = original_states
	user_rate_limiter._last_cleanup = original_last_cleanup
	user_rate_limiter.rate_limit = original_rate_limit


@pytest.fixture(autouse=True)
def mock_nearby_service():
	"""Patch the service to avoid making real HTTP calls to tankerkoenig."""
	with patch(
		"app.services.nearby_stations_service.NearbyStationsService.get_nearby_stations",
		new=AsyncMock(return_value=[]),
	) as mock:
		yield mock


class TestNearbyStationsRateLimiting:
	"""HTTP-level tests for rate limiting on the nearby stations endpoint."""

	async def test_rate_limit_exceeded_returns_429(
		self,
		authenticated_client: AsyncClient,
		test_user: User,
	):
		"""Hitting the limit should result in HTTP 429."""
		limit = 100  # default config

		# Use up all tokens
		for _ in range(limit):
			resp = await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
			assert resp.status_code == status.HTTP_200_OK

		# One more should be rate limited
		resp = await authenticated_client.get(
			"/api/v0/stations/nearby",
			params={"latitude": 52.52, "longitude": 13.405},
		)
		assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
		body = resp.json()
		assert body["error"] == "Rate limit exceeded"
		assert body["retry_after_seconds"] > 0

	async def test_429_includes_retry_after_header(
		self,
		authenticated_client: AsyncClient,
	):
		"""429 responses should have a Retry-After header (seconds as string)."""
		limit = 100
		for _ in range(limit):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		resp = await authenticated_client.get(
			"/api/v0/stations/nearby",
			params={"latitude": 52.52, "longitude": 13.405},
		)
		assert resp.status_code == status.HTTP_429_TOO_MANY_REQUESTS
		assert "Retry-After" in resp.headers
		assert int(resp.headers["Retry-After"]) >= 1

	async def test_per_user_limits_are_independent(
		self,
		authenticated_client: AsyncClient,
		second_user: User,
	):
		"""Different users should have separate rate limit buckets."""
		limit = 100

		# Exhaust first user
		for _ in range(limit):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		assert (
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
		).status_code == status.HTTP_429_TOO_MANY_REQUESTS

		# Switch to second user
		from app.auth import get_jwt_strategy

		strategy = get_jwt_strategy()
		token = await strategy.write_token(second_user)
		authenticated_client.headers["Authorization"] = f"Bearer {token}"

		# Should still have full quota
		resp = await authenticated_client.get(
			"/api/v0/stations/nearby",
			params={"latitude": 52.52, "longitude": 13.405},
		)
		assert resp.status_code == status.HTTP_200_OK

	async def test_status_endpoint_before_any_requests(
		self,
		authenticated_client: AsyncClient,
	):
		"""Status should report full quota before any usage."""
		resp = await authenticated_client.get("/api/v0/stations/rate-limit/status")
		assert resp.status_code == status.HTTP_200_OK
		data = resp.json()
		assert data["remaining"] == 100
		assert data["limit"] == 100
		assert data["is_cooldown"] is False
		assert data["window_seconds"] == 3600
		assert "reset_at" in data

	async def test_status_decrements_after_request(self, authenticated_client: AsyncClient):
		"""Remaining count should go down after each request."""
		initial = (await authenticated_client.get("/api/v0/stations/rate-limit/status")).json()["remaining"]

		await authenticated_client.get("/api/v0/stations/nearby", params={"latitude": 52.52, "longitude": 13.405})

		new_remaining = (await authenticated_client.get("/api/v0/stations/rate-limit/status")).json()["remaining"]
		assert new_remaining == initial - 1

	async def test_status_shows_cooldown_when_exhausted(
		self,
		authenticated_client: AsyncClient,
	):
		"""After exhausting the limit, status should indicate cooldown."""
		for _ in range(100):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		data = (await authenticated_client.get("/api/v0/stations/rate-limit/status")).json()
		assert data["remaining"] == 0
		assert data["is_cooldown"] is True
		assert data["reset_at"] is not None

	async def test_status_requires_auth(self, async_client: AsyncClient):
		"""Unauthorized calls to status endpoint should 401."""
		resp = await async_client.get("/api/v0/stations/rate-limit/status")
		assert resp.status_code == status.HTTP_401_UNAUTHORIZED

	async def test_nearby_endpoint_only_rate_limited_others_ok(
		self,
		authenticated_client: AsyncClient,
	):
		"""Only /nearby is rate limited; other endpoints work."""
		# Exhaust limit
		for _ in range(100):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		assert (
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
		).status_code == status.HTTP_429_TOO_MANY_REQUESTS

		# Other station endpoints still work
		assert (await authenticated_client.get("/api/v0/stations/")).status_code == status.HTTP_200_OK

	async def test_refill_after_time_passes(
		self,
		authenticated_client: AsyncClient,
		test_user: User,
	):
		"""After sufficient time, the token bucket refills and requests succeed."""
		# Exhaust the bucket
		for _ in range(100):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		# Confirm rate limited
		assert (
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
		).status_code == status.HTTP_429_TOO_MANY_REQUESTS

		# Simulate time passing by adjusting the last_update timestamp
		user_id = test_user.id
		state = user_rate_limiter._user_states[user_id]
		state.last_update -= 3600  # Pretend 1 hour passed

		# Should succeed now
		resp = await authenticated_client.get(
			"/api/v0/stations/nearby",
			params={"latitude": 52.52, "longitude": 13.405},
		)
		assert resp.status_code == status.HTTP_200_OK

	async def test_partial_usage_shows_correct_remaining(
		self,
		authenticated_client: AsyncClient,
	):
		"""Remaining count should accurately reflect used tokens."""
		for _ in range(50):
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)

		data = (await authenticated_client.get("/api/v0/stations/rate-limit/status")).json()
		assert data["remaining"] == 50

	async def test_burst_behavior(self, authenticated_client: AsyncClient):
		"""A burst up to the limit should all succeed."""
		limit = 100
		tasks = [
			authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
			for _ in range(limit)
		]
		responses = await asyncio.gather(*tasks)
		assert all(r.status_code == status.HTTP_200_OK for r in responses)

		assert (
			await authenticated_client.get(
				"/api/v0/stations/nearby",
				params={"latitude": 52.52, "longitude": 13.405},
			)
		).status_code == status.HTTP_429_TOO_MANY_REQUESTS


class TestUserBasedRateLimiterUnit:
	"""Tests on the rate limiter class in isolation."""

	async def test_initial_state_is_full_quota(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(rate_limit=10, time_window=60)
		st = limiter.get_status(42)
		assert st["remaining"] == 10
		assert st["is_cooldown"] is False

	async def test_allows_up_to_limit_then_denies(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(rate_limit=3, time_window=60)
		uid = 1
		for _ in range(3):
			assert (await limiter.check(uid))[0] is True
		assert (await limiter.check(uid))[0] is False

	async def test_status_reflects_usage(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(rate_limit=5, time_window=60)
		uid = 77
		for _ in range(2):
			await limiter.check(uid)
		st = limiter.get_status(uid)
		assert st["remaining"] == 3

	async def test_multiple_users_separate(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(rate_limit=2, time_window=60)
		await limiter.check(10)
		await limiter.check(10)
		assert (await limiter.check(10))[0] is False
		# User 11 untouched
		assert (await limiter.check(11))[0] is True

	async def test_refill_replenishes_tokens(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		# 2 tokens capacity, window 2 sec => refill rate = 1 token/sec
		limiter = UserBasedRateLimiter(rate_limit=2, time_window=2)
		uid = 555

		# Mock time.monotonic to control timing
		base_time = 1000.0
		with patch("time.monotonic", return_value=base_time):
			await limiter.check(uid)  # tokens: 2 -> 1, last_update = 1000

		# Advance time by 0 seconds (no refill)
		with patch("time.monotonic", return_value=base_time):
			await limiter.check(uid)  # tokens: 1 -> 0, last_update = 1000

		state = limiter._user_states[uid]
		assert state.tokens == 0

		# Move time forward 0.5 seconds: should have ~0.5 tokens (<1), still denied
		state.last_update = base_time - 0.5
		with patch("time.monotonic", return_value=base_time):
			allowed, _ = await limiter.check(uid)
		assert allowed is False

		# After another 0.6 seconds (total 1.1 from last_update), refill >1 token, should allow
		state.last_update = base_time - 1.1
		with patch("time.monotonic", return_value=base_time):
			allowed, _ = await limiter.check(uid)
		assert allowed is True

	async def test_tokens_never_exceed_limit(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(rate_limit=5, time_window=1)  # 5/sec
		uid = 777
		await limiter.check(uid)
		state = limiter._user_states[uid]
		state.tokens = 1.0
		state.last_update -= 100  # 100 seconds -> would refill 500, capped at 5
		await limiter.check(uid)
		# tokens should become 4 (since we used 1), not overflow
		assert state.tokens == 4.0

	async def test_cleanup_removes_inactive_users(self):
		from app.services.rate_limiter import UserBasedRateLimiter

		limiter = UserBasedRateLimiter(
			rate_limit=10,
			time_window=60,
			stale_timeout=1,  # 1 s
			cleanup_interval=1,
		)
		uid1, uid2 = 111, 222
		await limiter.check(uid1)
		await limiter.check(uid2)

		# Make uid1 stale
		limiter._user_states[uid1].last_update -= 10
		# Force cleanup
		limiter._last_cleanup -= 100
		await limiter._cleanup_stale_users()

		assert uid1 not in limiter._user_states
		assert uid2 in limiter._user_states
