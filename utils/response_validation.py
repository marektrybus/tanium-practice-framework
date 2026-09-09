from typing import Any

from requests import Response


def assert_status_code(response: Any, expected_status: int) -> None:
    assert response.status_code == expected_status, (
        f"Expected HTTP {expected_status}, "
        f"but received HTTP {response.status_code}. "
        f"Response body: {response.text}"
    )


def assert_required_fields(
        payload: dict[str, Any], 
        required_fields: list[str],
    ) -> None:
    missing_fields = [field for field in required_fields if field not in payload]

    assert not missing_fields, (
        f"Response is missing required fields: {missing_fields}. "
        f"Actual response: {payload}"
    )

def get_json_object(response: Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError as error:
        raise AssertionError(
            "Response does not contain valid JSON. "
            f"HTTP status: {response.status_code}. "
            f"Response body: {response.text}"
        ) from error

    if not isinstance(payload, dict):
        raise TypeError(
            "Response JSON must be an object, "
            f"but was decoded as: {type(payload).__name__}. "
            f"Actual response: {payload}"
        )
    
    return payload