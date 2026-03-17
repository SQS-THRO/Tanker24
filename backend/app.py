import uvicorn
import sys
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from router.example import router as example_router
from database import create_db_and_tables

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up...")
        logger.info("connecting to database and creating tables if not exist")
        await create_db_and_tables()
        logger.info("Startup complete")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise  # Re-raise the exception to see the error on startup
    finally:
        logger.info("Shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(example_router, prefix="/api/v0")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
