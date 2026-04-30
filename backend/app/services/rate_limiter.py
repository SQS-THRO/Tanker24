import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, UTC
from typing import TypedDict, Dict

from app.config import settings


class RateLimiterStatus(TypedDict):
	"""Type definition for rate limiter status response."""

	remaining: int
	reset_at: str
	limit: int
	window_seconds: int
	is_cooldown: bool


class RateLimiter:
	"""
	Simple token bucket rate limiter (used for external API calls).
	This is a global shared rate limiter, not per-user.
	"""

	def __init__(self, rate_limit: int, time_window: float = 60.0):
		self.rate_limit = rate_limit
		self.time_window = time_window
		self.tokens: float = rate_limit
		self.last_update = time.monotonic()
		self._lock = asyncio.Lock()

	async def acquire(self) -> bool:
		"""Try to acquire a token without waiting. Returns True on success."""
		async with self._lock:
			now = time.monotonic()
			elapsed = now - self.last_update
			self.tokens = min(
				self.rate_limit,
				self.tokens + elapsed * (self.rate_limit / self.time_window),
			)
			self.last_update = now

			if self.tokens >= 1:
				self.tokens -= 1
				return True
			return False

	async def wait_for_token(self) -> None:
		"""Wait until a token becomes available."""
		while True:
			if await self.acquire():
				return
			await asyncio.sleep(0.1)


@dataclass
class UserRateLimitState:
	"""State for a single user's rate limiting bucket."""

	tokens: float = field(default=0.0)
	last_update: float = field(default_factory=time.monotonic)


class UserBasedRateLimiter:
	"""
	Per-user rate limiter using the token bucket algorithm.

	Each user has an independent bucket that refills at a steady rate.
	This class is thread-safe for asyncio concurrency.
	"""

	def __init__(
		self,
		rate_limit: int,
		time_window: float = 3600.0,
		cleanup_interval: float = 300.0,
		stale_timeout: float = 3600.0,
	):
		self.rate_limit = rate_limit
		self.time_window = time_window
		self.refill_rate = rate_limit / time_window
		self.cleanup_interval = cleanup_interval
		self.stale_timeout = stale_timeout

		self._user_states: Dict[int, UserRateLimitState] = {}
		self._last_cleanup = time.monotonic()
		self._lock = asyncio.Lock()

	async def _cleanup_stale_users(self):
		"""Remove users who haven't made requests within the stale timeout."""
		now = time.monotonic()
		cutoff = now - self.stale_timeout
		stale_users = [uid for uid, state in self._user_states.items() if state.last_update < cutoff]
		for uid in stale_users:
			del self._user_states[uid]
		self._last_cleanup = now

	async def check(self, user_id: int) -> tuple[bool, float]:
		"""
		Check if a request is allowed without blocking.

		Modifies the user's state (refills tokens and may deduct one).

		Returns:
			(allowed, wait_time): if allowed, wait_time is 0; else seconds until a token is available.
		"""
		async with self._lock:
			now = time.monotonic()

			# Periodic cleanup of stale users to prevent memory leaks
			if now - self._last_cleanup > self.cleanup_interval:
				await self._cleanup_stale_users()

			# Get or create state for this user
			state = self._user_states.get(user_id)
			if state is None:
				# New user starts with a full bucket
				state = UserRateLimitState(tokens=self.rate_limit, last_update=now)
				self._user_states[user_id] = state

			# Refill tokens based on elapsed time
			elapsed = now - state.last_update
			state.tokens = min(
				self.rate_limit,
				state.tokens + elapsed * self.refill_rate,
			)
			state.last_update = now

			# Try to consume a token
			if state.tokens >= 1:
				state.tokens -= 1
				return True, 0.0

			# Not enough tokens: compute wait time until next token
			deficit = 1.0 - state.tokens
			wait_time = deficit / self.refill_rate
			return False, wait_time

	async def wait_for_token(self, user_id: int) -> float:
		"""
		Wait until a token becomes available for the user.

		Returns the number of seconds actually waited.
		"""
		total_waited = 0.0
		while True:
			allowed, wait_time = await self.check(user_id)
			if allowed:
				return total_waited
			sleep = min(wait_time, 0.1)
			await asyncio.sleep(sleep)
			total_waited += sleep

	def get_status(self, user_id: int) -> RateLimiterStatus:
		"""
		Get current rate-limit status for a user without modifying state.

		Returns a dictionary with:
			remaining (int): tokens left
			reset_at (str): ISO-8601 timestamp when next token will be available
			limit (int): maximum tokens
			window_seconds (int): duration of the window in seconds
			is_cooldown (bool): True if no tokens are currently available
		"""
		state = self._user_states.get(user_id)
		now = time.monotonic()

		if state is None:
			return {
				"remaining": self.rate_limit,
				"reset_at": (datetime.now(UTC) + timedelta(seconds=self.time_window)).isoformat(),
				"limit": self.rate_limit,
				"window_seconds": int(self.time_window),
				"is_cooldown": False,
			}

		# Estimate current tokens without updating state
		elapsed = now - state.last_update
		current_tokens = min(
			self.rate_limit,
			state.tokens + elapsed * self.refill_rate,
		)

		is_cooldown = current_tokens < 1
		remaining = max(0, int(current_tokens))

		if is_cooldown:
			deficit = 1.0 - current_tokens
			wait_time = deficit / self.refill_rate
			reset_at = (datetime.now(UTC) + timedelta(seconds=wait_time)).isoformat()
		else:
			reset_at = (datetime.now(UTC) + timedelta(seconds=self.time_window)).isoformat()

		return {
			"remaining": remaining,
			"reset_at": reset_at,
			"limit": self.rate_limit,
			"window_seconds": int(self.time_window),
			"is_cooldown": is_cooldown,
		}


# Global per-user rate limiter for the nearby stations endpoint
user_rate_limiter = UserBasedRateLimiter(
	rate_limit=settings.nearby_stations_rate_limit_per_hour,
	time_window=3600.0,  # 1 hour
)

# Global rate limiter for the external Tankerkoenig API (shared, not per-user)
global_rate_limiter = RateLimiter(
	rate_limit=settings.tankerkoenig_rate_limit_per_minute,
	time_window=60.0,
)
