from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.main import lifespan


@pytest.mark.asyncio
class TestLifespan:
	async def test_startup_calls_setup_logging(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		with (
			patch("app.main.setup_logging") as mock_setup_logging,
			patch("app.main.init_db", AsyncMock()) as mock_init_db,
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()) as mock_sync_keys,
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger"),
		):
			async with lifespan(MagicMock()):
				pass

		mock_setup_logging.assert_called_once()

	async def test_startup_calls_init_db(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		with (
			patch("app.main.setup_logging"),
			patch("app.main.init_db", AsyncMock()) as mock_init_db,
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()),
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger"),
		):
			async with lifespan(MagicMock()):
				pass

		mock_init_db.assert_awaited_once()

	async def test_startup_calls_sync_invitation_keys(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		with (
			patch("app.main.setup_logging"),
			patch("app.main.init_db", AsyncMock()),
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()) as mock_sync_keys,
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger"),
		):
			async with lifespan(MagicMock()):
				pass

		mock_sync_keys.assert_awaited_once_with(mock_session)

	async def test_startup_logs_app_info(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		with (
			patch("app.main.setup_logging"),
			patch("app.main.init_db", AsyncMock()),
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()),
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger") as mock_logger,
			patch("app.main.settings.app_name", "TestApp"),
			patch("app.main.settings.app_version", "2.0.0"),
			patch("app.main.settings.db_type", "sqlite"),
		):
			async with lifespan(MagicMock()):
				pass

		mock_logger.info.assert_any_call("Starting %s v%s", "TestApp", "2.0.0")
		mock_logger.info.assert_any_call("Database: %s", "sqlite")
		mock_logger.info.assert_any_call("Application startup complete")

	async def test_shutdown_logs_message(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		with (
			patch("app.main.setup_logging"),
			patch("app.main.init_db", AsyncMock()),
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()),
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger") as mock_logger,
		):
			async with lifespan(MagicMock()):
				pass

		mock_logger.info.assert_any_call("Application shutting down")

	async def test_lifespan_yields_control(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		yielded = False

		with (
			patch("app.main.setup_logging"),
			patch("app.main.init_db", AsyncMock()),
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", AsyncMock()),
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger"),
		):
			async with lifespan(MagicMock()):
				yielded = True

		assert yielded, "lifespan should yield control to the application"

	async def test_startup_ordering(self):
		mock_session = AsyncMock()
		mock_session.__aenter__.return_value = mock_session

		call_order = []

		def track_setup_logging():
			call_order.append("setup_logging")

		async def track_init_db():
			call_order.append("init_db")

		async def track_sync_keys(*args, **kwargs):
			call_order.append("sync_invitation_keys")

		with (
			patch("app.main.setup_logging", side_effect=track_setup_logging),
			patch("app.main.init_db", side_effect=track_init_db),
			patch("app.main.async_session_maker", return_value=mock_session),
			patch("app.main.sync_invitation_keys", side_effect=track_sync_keys),
			patch("app.main.seed_fuel_types", AsyncMock()),
			patch("app.main.logger"),
		):
			async with lifespan(MagicMock()):
				pass

		assert call_order == ["setup_logging", "init_db", "sync_invitation_keys"]
