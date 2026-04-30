from unittest.mock import Mock

from app.dependencies import (
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
