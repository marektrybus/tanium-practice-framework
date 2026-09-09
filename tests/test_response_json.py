from unittest.mock import Mock

import pytest
from requests import Response

from utils.response_validation import get_json_object


@pytest.mark.unit
def test_get_json_object_fails_with_dignostics_for_invalid_json() -> None:
    response = Mock(spec=Response)
    response.status_code = 502
    response.text = "<html>Bad Gateway</html>"
    response.json.side_effect = ValueError("Invalid JSON")

    with pytest.raises(AssertionError, match="does not contain valid JSON") as error:
        get_json_object(response)

    assert "HTTP status: 502" in str(error.value)

@pytest.mark.unit
def test_get_json_object_fails_when_json_is_not_an_object() -> None:
    response = Mock(spec=Response)
    response.json.return_value = ["unexpected", "list"]

    with pytest.raises(TypeError, match="Response JSON must be an object"):
        get_json_object(response)