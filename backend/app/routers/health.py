from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}


@router.get("/")
async def root() -> dict[str, str]:
    return {"message": f"Welcome to {settings.app_name} v{settings.app_version}"}
