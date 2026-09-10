from unittest.mock import Mock, patch

import pytest
from requests import Response

from api.jsonplaceholder_client import JsonPlaceholderClient


@pytest.mark.unit
@patch("api.jsonplaceholder_client.requests.Session")
def test_get_user_send_expected_request(
    session_factory: Mock,
) -> None:
    session = session_factory.return_value
    expected_response = Mock(spec=Response)

    session.get.return_value = expected_response

    client = JsonPlaceholderClient(
        base_url="https://jsonplaceholder.typicode.com/",
    )

    actual_response = client.get_user(user_id=7)

    assert actual_response is expected_response
    session.get.assert_called_once_with(
        url="https://jsonplaceholder.typicode.com/users/7",
        timeout=10,
    )

    client.close()

    session.close.assert_called_once_with()

@pytest.mark.unit
@patch("api.jsonplaceholder_client.requests.Session")
def test_client_sets_bearer_token_when_token_is_provided(
    session_factory: Mock,
) -> None:
    session = session_factory.return_value

    JsonPlaceholderClient(
        base_url="https://jsonplaceholder.typicode.com/users/7",
        token="test-token"
    )

    session.headers.update.assert_called_once_with(
        {"Authorization": "Bearer test-token"},
    )
