from unittest.mock import Mock, MagicMock

from app.dependencies import (
	get_current_user_with_request_state,
	get_flat_export_data_service,
	get_nested_export_data_service,
)
from app.services.export_data_service import (
	ExportDataService,
	FlatExportDataService,
	NestedExportDataService,
)


class TestDependencies:
	def test_get_nested_export_data_service_returns_nested_service(self):
		db = Mock()

		service = get_nested_export_data_service(db)

		assert isinstance(service, NestedExportDataService)
		assert isinstance(service, ExportDataService)
		assert service.db is db

	def test_get_flat_export_data_service_returns_flat_service(self):
		db = Mock()

		service = get_flat_export_data_service(db)

		assert isinstance(service, FlatExportDataService)
		assert isinstance(service, ExportDataService)
		assert service.db is db

	def test_get_current_user_with_request_state_sets_user_on_state(self):
		request = MagicMock()
		user = MagicMock()

		result = get_current_user_with_request_state(request, user)

		assert request.state.user is user
		assert result is user
