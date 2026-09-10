import pytest
from playwright.sync_api import Page, expect

from api.local_todo_client import LocalTodoClient
from pages.local_todo_page import LocalTodoPage


@pytest.mark.integration
def test_todo_created_by_api_is_visible_in_ui(
    page: Page,
    local_app_url: str,
) -> None:
    api_client = LocalTodoClient(local_app_url)
    todo_title = "Created through the API"

    create_response = api_client.create_todo(todo_title)

    assert create_response.status_code == 201

    todo_page = LocalTodoPage(page, local_app_url)
    todo_page.open()

    expect(todo_page.todo_with_text(todo_title)).to_have_count(1)
    expect(todo_page.todo_with_text(todo_title)).to_be_visible()