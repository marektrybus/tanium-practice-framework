import pytest

from utils.response_validation import assert_required_fields


@pytest.mark.unit
def test_required_fields_are_present() -> None:
    user = {
        "id": 42,
        "name": "Anna",
        "email": "anna@example.com",
    }

    assert_required_fields(user, ["id", "name", "email"])