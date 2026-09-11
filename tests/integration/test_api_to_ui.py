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

@pytest.mark.integration
def test_todo_created_by_ui_is_available_through_api(
    page: Page,
    local_app_url: str,
) -> None:
    todo_title = "Created through the UI"
    todo_page = LocalTodoPage(page, local_app_url)
    api_client = LocalTodoClient(local_app_url)

    todo_page.open()
    todo_page.add_todo(todo_title)

    expect(todo_page.todo_with_text(todo_title)).to_be_visible()

    get_response = api_client.get_todos()

    assert get_response.status_code == 200
    assert get_response.json() == [
        {"id": 1, "title": todo_title},
    ]