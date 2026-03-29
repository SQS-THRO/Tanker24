import asyncio
import time
from app.config import settings


class RateLimiter:
	def __init__(self, rate_limit: int, time_window: float = 60.0):
		self.rate_limit = rate_limit
		self.time_window = time_window
		self.tokens = rate_limit
		self.last_update = time.monotonic()
		self._lock = asyncio.Lock()

	async def acquire(self) -> bool:
		async with self._lock:
			now = time.monotonic()
			elapsed = now - self.last_update
			self.tokens = min(self.rate_limit, self.tokens + elapsed * (self.rate_limit / self.time_window))
			self.last_update = now

			if self.tokens >= 1:
				self.tokens -= 1
				return True
			return False

	async def wait_for_token(self) -> None:
		while True:
			if await self.acquire():
				return
			await asyncio.sleep(0.1)


global_rate_limiter = RateLimiter(
	rate_limit=settings.tankerkoenig_rate_limit_per_minute,
	time_window=60.0
)
