from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.database import async_session_maker, init_db
from app.invitation_keys import sync_invitation_keys
from app.limiter import limiter
from app.routers import auth, health, stations, export


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	await init_db()
	async with async_session_maker() as session:
		await sync_invitation_keys(session)
	yield


app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
)

# Store limiter in app state
app.state.limiter = limiter

# Add SlowAPI middleware for rate limiting
app.add_middleware(SlowAPIMiddleware)


# Add exception handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
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
	allow_origins=settings.CORSorigins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)
