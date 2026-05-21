import logging
import re

from app.logging_config import ApikeyFilter, setup_logging


class TestApikeyFilter:
	def test_filter_passes_through_normal_messages(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord("test", logging.INFO, "", 0, "normal message", (), None)
		assert filter_obj.filter(record)
		assert record.msg == "normal message"

	def test_filter_redacts_apikey_in_url(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord(
			"test", logging.INFO, "", 0,
			"list.php?lat=52.5&apikey=secret123&type=all",
			(), None,
		)
		assert filter_obj.filter(record)
		assert "apikey=***" in str(record.msg)
		assert "secret123" not in str(record.msg)

	def test_filter_redacts_apikey_case_insensitive(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord(
			"test", logging.INFO, "", 0,
			"list.php?lat=52.5&APIKEY=secret456",
			(), None,
		)
		assert filter_obj.filter(record)
		assert "secret456" not in str(record.msg)

	def test_filter_redacts_apikey_with_special_chars(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord(
			"test", logging.INFO, "", 0,
			"list.php?apikey=abc-def_ghi&lat=52.5",
			(), None,
		)
		assert filter_obj.filter(record)
		assert "apikey=***" in str(record.msg)
		assert "abc-def_ghi" not in str(record.msg)

	def test_filter_handles_none_message(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord("test", logging.INFO, "", 0, None, (), None)
		assert filter_obj.filter(record)
		assert record.msg is None

	def test_filter_handles_empty_message(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord("test", logging.INFO, "", 0, "", (), None)
		assert filter_obj.filter(record)
		assert record.msg == ""

	def test_filter_returns_true_always(self):
		filter_obj = ApikeyFilter()
		record = logging.LogRecord("test", logging.INFO, "", 0, "any message", (), None)
		assert filter_obj.filter(record) is True


class TestSetupLogging:
	def test_setup_logging_sets_httpx_to_warning(self):
		setup_logging()
		httpx_logger = logging.getLogger("httpx")
		assert httpx_logger.level == logging.WARNING

	def test_setup_logging_adds_apikey_filter_to_app_logger(self):
		setup_logging()
		app_logger = logging.getLogger("app")
		filter_names = {f.name for f in app_logger.filters}
		assert any(isinstance(f, ApikeyFilter) for f in app_logger.filters)

	def test_setup_logging_adds_apikey_filter_to_uvicorn_logger(self):
		setup_logging()
		uvicorn_logger = logging.getLogger("uvicorn")
		assert any(isinstance(f, ApikeyFilter) for f in uvicorn_logger.filters)

	def test_setup_logging_adds_apikey_filter_to_httpx_logger(self):
		setup_logging()
		httpx_logger = logging.getLogger("httpx")
		assert any(isinstance(f, ApikeyFilter) for f in httpx_logger.filters)
