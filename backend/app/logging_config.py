import logging
import re
import sys

from app.config import settings


class ApikeyFilter(logging.Filter):
	def filter(self, record: logging.LogRecord) -> bool:
		if record.msg and "apikey" in str(record.msg).lower():
			record.msg = re.sub(r"apikey=[^&\s]+", "apikey=***", str(record.msg))
		return True


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
	logging.getLogger("httpx").setLevel(logging.WARNING)

	for logger_name in ("app", "uvicorn", "httpx"):
		logging.getLogger(logger_name).addFilter(ApikeyFilter())
