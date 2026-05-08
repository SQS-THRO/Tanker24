import logging
import sys

from app.config import settings


def setup_logging() -> None:
	level = getattr(logging, settings.log_level.upper(), logging.INFO)

	handler = logging.StreamHandler(sys.stdout)
	handler.setFormatter(
		logging.Formatter(
			"%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
			datefmt="%Y-%m-%d %H:%M:%S",
		)
	)

	logging.basicConfig(level=level, handlers=[handler], force=True)

	logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
	logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO if settings.debug else logging.WARNING)
