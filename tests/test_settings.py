import pytest

from config.settings import get_api_base_url, get_api_token


@pytest.mark.unit
def test_get_api_base_url_uses_default_value(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("API_BASE_URL", raising=False)

    assert get_api_base_url() == "https://jsonplaceholder.typicode.com"

@pytest.mark.unit
def test_get_api_base_url_uses_envirnment_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("API_BASE_URL", "https://test.example.com/")

    assert get_api_base_url() == "https://test.example.com"

@pytest.mark.unit
def test_get_api_token_returns_none_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("API_TOKEN", raising=False)

    assert get_api_token() is None