import logging
import time

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.database import async_session_maker, init_db
from app.invitation_keys import sync_invitation_keys
from app.limiter import limiter
from app.logging_config import setup_logging
from app.routers import auth, health, stations, export

logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	setup_logging()
	logger.info("Starting %s v%s", settings.app_name, settings.app_version)
	logger.info("Database: %s", settings.db_type)
	await init_db()
	async with async_session_maker() as session:
		await sync_invitation_keys(session)
	logger.info("Application startup complete")
	yield
	logger.info("Application shutting down")


app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		start = time.perf_counter()
		response = await call_next(request)
		duration_ms = (time.perf_counter() - start) * 1000
		logger.info(
			"%s %s -> %d (%.1fms)",
			request.method,
			request.url.path,
			response.status_code,
			duration_ms,
		)
		return response


app.add_middleware(RequestLoggingMiddleware)

# Store limiter in app state
app.state.limiter = limiter

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)


# Add exception handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
	logger.warning("Rate limit exceeded for %s %s", request.method, request.url.path)
	return JSONResponse(
		status_code=429,
		content={"detail": "Rate limit exceeded. Please try again later."},
	)


api_router = APIRouter(prefix="/api/v0")

api_router.include_router(auth.auth_router, prefix="/auth/jwt", tags=["auth"])
api_router.include_router(auth.register_router, prefix="/auth", tags=["auth"])
api_router.include_router(auth.users_router, prefix="/users", tags=["users"])
api_router.include_router(stations.router)
api_router.include_router(export.router)

app.include_router(health.router)
app.include_router(api_router)

app.add_middleware(
	CORSMiddleware,
	allow_origins=settings.cors_origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
