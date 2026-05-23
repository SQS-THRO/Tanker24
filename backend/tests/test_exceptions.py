import pytest

from app.exceptions.exceptions import FillingNotFoundException

@pytest.mark.asyncio
class TestFillingNotFoundException:
    def test_filling_not_found_exception_stores_filling_id(self) -> None:
        exception = FillingNotFoundException(42)

        assert exception.filling_id == 42


    def test_filling_not_found_exception_message(self) -> None:
        exception = FillingNotFoundException(42)

        assert str(exception) == "Filling with ID 42 not found"


    def test_filling_not_found_exception_is_exception(self) -> None:
        exception = FillingNotFoundException(42)

        assert isinstance(exception, Exception)