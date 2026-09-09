from collections.abc import Iterator

import pytest
from playwright.sync_api import Page

from api.jsonplaceholder_client import JsonPlaceholderClient
from config.settings import get_api_base_url, get_api_token
from pages.todo_page import TodoPage


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return get_api_base_url()

@pytest.fixture
def api_client(api_base_url: str) -> Iterator[JsonPlaceholderClient]:
    client = JsonPlaceholderClient(
        base_url=api_base_url,
        token=get_api_token(),
        )

    yield client

    client.close()

@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    todo_page = TodoPage(page)
    todo_page.open()

    return todo_page