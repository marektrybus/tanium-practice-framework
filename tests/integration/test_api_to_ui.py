import pytest
from playwright.sync_api import expect

from api.local_todo_client import LocalTodoClient
from pages.local_todo_page import LocalTodoPage


@pytest.mark.integration
def test_todo_created_by_api_is_visible_in_ui(
    local_todo_client: LocalTodoClient,
    local_todo_page: LocalTodoPage,
) -> None:
    todo_title = "Created through the API"

    create_response = local_todo_client.create_todo(todo_title)

    assert create_response.status_code == 201

    local_todo_page.open()

    expect(local_todo_page.todo_with_text(todo_title)).to_have_count(1)
    expect(local_todo_page.todo_with_text(todo_title)).to_be_visible()


@pytest.mark.integration
def test_todo_created_by_ui_is_available_through_api(
    local_todo_page: LocalTodoPage,
    local_todo_client: LocalTodoClient,
) -> None:
    todo_title = "Created through the UI"

    local_todo_page.open()

    local_todo_page.add_todo(todo_title)

    expect(local_todo_page.todo_with_text(todo_title)).to_be_visible()

    get_response = local_todo_client.get_todos()

    assert get_response.status_code == 200
    assert get_response.json() == [
        {"id": 1, "title": todo_title},
    ]


@pytest.mark.integration
def test_todo_deleted_by_ui_is_removed_through_api(
    local_todo_page: LocalTodoPage,
    local_todo_client: LocalTodoClient,
) -> None:
    todo_title = "Todo deleted through the UI"

    create_response = local_todo_client.create_todo(todo_title)

    assert create_response.status_code == 201

    local_todo_page.open()

    expect(local_todo_page.todo_with_text(todo_title)).to_be_visible()

    local_todo_page.delete_todo(todo_title)

    expect(local_todo_page.todo_with_text(todo_title)).to_have_count(0)

    get_response = local_todo_client.get_todos()

    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.integration
def test_todo_remains_visible_when_delete_request_fails(
    local_todo_client: LocalTodoClient,
    local_todo_page: LocalTodoPage,
) -> None:
    todo_title = "Todo that cannot be deleted"

    create_response = local_todo_client.create_todo(todo_title)

    assert create_response.status_code == 201
    created_todo = create_response.json()

    local_todo_page.open()

    local_todo_page.page.route(
        "**/api/todos/*",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body='{"detail": "Database unavilable"}',
        ),
    )

    local_todo_page.delete_todo(todo_title)

    expect(local_todo_page.todo_with_text(todo_title)).to_be_visible()
    expect(local_todo_page.error_message).to_have_text(
        "Could not delete todo. Please try again."
    )

    get_response = local_todo_client.get_todos()

    assert get_response.status_code == 200
    assert get_response.json() == [created_todo]


@pytest.mark.integration
def test_client_gets_protected_todo_with_bearer_token(
    local_todo_client: LocalTodoClient,
) -> None:

    create_response = local_todo_client.create_todo("Protected integration todo")

    assert create_response.status_code == 201
    created_todo = create_response.json()

    get_response = local_todo_client.get_todo(created_todo["id"])

    assert get_response.status_code == 200
    assert get_response.json() == created_todo


@pytest.mark.integration
def test_client_without_token_can_create_public_todo(
    unauthenticated_local_todo_client: LocalTodoClient,
) -> None:
    response = unauthenticated_local_todo_client.create_todo(
        "Public todo",
    )

    assert response.status_code == 201
    assert response.request.headers.get("Authorization") is None
