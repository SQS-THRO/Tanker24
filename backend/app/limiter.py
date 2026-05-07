from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def get_rate_limit_key(request: Request) -> str:
	"""
	Generate a rate limit key based on the authenticated user.
	Falls back to IP address if user is not found in request state.
	"""
	# Try to get user from request state (set by get_current_user_with_request_state dependency)
	user = getattr(request.state, "user", None)
	if user and hasattr(user, "id"):
		return f"user:{user.id}"
	# Fallback to IP address
	return get_remote_address(request)


# Initialize limiter with memory storage (default)
# The storage_uri="memory://" explicitly uses in-memory storage
limiter = Limiter(
	key_func=get_rate_limit_key,
	storage_uri="memory://",
)
