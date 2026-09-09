import pytest

from api.jsonplaceholder_client import JsonPlaceholderClient
from utils.response_validation import (
    assert_required_fields,
    assert_status_code,
    get_json_object,
)


@pytest.mark.api
@pytest.mark.parametrize(
    ("user_id", "expected_username"),
    [
        (1, "Bret"),
        (2, "Antonette"),
        (3, "Samantha"),
    ],
)
def test_get_existing_user_retrurns_expected_data(
        api_client: JsonPlaceholderClient,
        user_id: int,
        expected_username: str,
    ) -> None:
    response = api_client.get_user(user_id=user_id)

    assert_status_code(response, expected_status=200)

    user = get_json_object(response)

    assert_required_fields(user, ["id", "name", "username", "email"])
    assert user["id"] == user_id
    assert user["username"] == expected_username


