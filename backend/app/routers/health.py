from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get(
	"/health",
	summary="Health check",
	description="Check if the application is running and healthy. Returns the application name and version.",
)
async def health_check() -> dict[str, str]:
	return {
		"status": "healthy",
		"app": settings.app_name,
		"version": settings.app_version,
	}


@router.get(
	"/",
	summary="Root endpoint",
	description="Welcome endpoint that returns a greeting message with the application name and version.",
)
async def root() -> dict[str, str]:
	return {"message": f"Welcome to {settings.app_name} v{settings.app_version}"}
