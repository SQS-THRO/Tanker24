import pathlib
import pytest

from pytestarch import get_evaluable_architecture, Rule

class TestArchitecture:
    @pytest.fixture(scope="module")
    def arch(self):
        root = pathlib.Path(__file__).resolve().parents[1]
        src = root / "app"
        return get_evaluable_architecture(str(root), str(src))

    def test_service_must_not_import_routers(self, arch):
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of("backend.app.services")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of("backend.app.routers")
        )
        rule.assert_applies(arch)

    def test_schemas_must_not_import_routers(self, arch):
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of("backend.app.schemas")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of("backend.app.routers")
        )
        rule.assert_applies(arch)

    def test_dtos_must_not_import_routers(self, arch):
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of("backend.app.dtos")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of("backend.app.routers")
        )
        rule.assert_applies(arch)

    def test_dtos_must_not_import_services(self, arch):
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of("backend.app.dtos")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of("backend.app.services")
        )
        rule.assert_applies(arch)

    def test_schemas_must_not_import_services(self, arch):
        rule = (
            Rule()
            .modules_that()
            .are_sub_modules_of("backend.app.schemas")
            .should_not()
            .import_modules_that()
            .are_sub_modules_of("backend.app.services")
        )
        rule.assert_applies(arch)
