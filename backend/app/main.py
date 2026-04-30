from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.database import async_session_maker, init_db
from app.invitation_keys import sync_invitation_keys
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
	"""Custom exception handler that returns detail directly for dict details."""
	if isinstance(exc.detail, dict):
		return JSONResponse(
			status_code=exc.status_code,
			content=exc.detail,
			headers=exc.headers,
		)
	return JSONResponse(
		status_code=exc.status_code,
		content={"detail": exc.detail},
		headers=exc.headers,
	)
