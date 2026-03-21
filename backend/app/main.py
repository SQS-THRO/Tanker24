from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routers import auth, health, stations


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
	await init_db()
	yield


app = FastAPI(
	title=settings.app_name,
	version=settings.app_version,
	lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(auth.auth_router, prefix="/auth/jwt", tags=["auth"])
app.include_router(auth.register_router, prefix="/auth", tags=["auth"])
app.include_router(auth.users_router, prefix="/users", tags=["users"])
app.include_router(stations.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORSorigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)