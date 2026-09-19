import pytest
from fastapi.testclient import TestClient

from app.main import app, todos

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_todos() -> None:
    todos.clear()


@pytest.fixture(autouse=True)
def configure_todo_api_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TODO_API_TOKEN", "test-token")


@pytest.mark.local_api
def test_create_todo_and_retrieve_it() -> None:
    create_response = client.post(
        "/api/todos",
        json={"title": "Prepare integration test"},
    )

    assert create_response.status_code == 201
    created_todo = create_response.json()
    assert created_todo["title"] == "Prepare integration test"

    get_response = client.get("/api/todos")

    assert get_response.status_code == 200
    assert get_response.json() == [created_todo]


@pytest.mark.local_api
@pytest.mark.parametrize(
    "invalid_title",
    [
        "",
        "   ",
        "x" * 101,
    ],
    ids=["empty", "whitespace-only", "too-long"],
)
def test_create_todo_rejects_invalid_title(invalid_title: str) -> None:

    response = client.post(
        "/api/todos",
        json={"title": invalid_title},
    )

    assert response.status_code == 422


@pytest.mark.local_api
def test_create_todo_strips_surrounding_whitespace() -> None:
    response = client.post("/api/todos", json={"title": "   sdf   "})

    assert response.status_code == 201
    assert response.json()["title"] == "sdf"


@pytest.mark.local_api
def test_delete_existing_todo_removes_it() -> None:
    create_response = client.post("/api/todos", json={"title": "todo to be deleted"})

    todo_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/todos/{todo_id}")

    assert delete_response.status_code == 204

    get_response = client.get("/api/todos")

    assert get_response.status_code == 200
    assert get_response.json() == []


@pytest.mark.local_api
def test_delete_missing_todo_returns_not_found() -> None:
    response = client.delete("/api/todos/999")

    assert response.status_code == 404


@pytest.mark.local_api
def test_todo_page_renders_todo_and_escapes_html() -> None:
    unsafe_title = "<img src=x onerror=alert(1)>"

    create_response = client.post(
        "/api/todos",
        json={"title": unsafe_title},
    )

    assert create_response.status_code == 201

    page_response = client.get("/")

    assert page_response.status_code == 200
    assert 'data-testid="new-todo-input"' in page_response.text
    assert 'data-testid="add-todo"' in page_response.text
    assert 'data-testid="todo-item"' in page_response.text
    assert 'data-testid="delete-todo"' in page_response.text
    assert "&lt;img src=x onerror=alert(1)&gt;" in page_response.text
    assert unsafe_title not in page_response.text


@pytest.mark.local_api
def test_get_todo_requires_authorization() -> None:
    response = client.get("/api/todos/1")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"
    assert response.json() == {
        "detail": "Authorization header is required.",
    }


@pytest.mark.local_api
@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer wrong-token",
        "Token test-token",
    ],
    ids=[
        "wrong-token",
        "wrong-scheme",
    ],
)
def test_get_todo_rejects_invalid_authorization(
    authorization: str,
) -> None:
    response = client.get(
        "/api/todos/1",
        headers={"Authorization": authorization},
    )

    assert response.status_code == 403


@pytest.mark.local_api
def test_get_missing_todo_returns_not_found_for_valid_token() -> None:
    response = client.get(
        "/api/todos/999",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 404


@pytest.mark.local_api
def test_get_todo_returns_todo_for_valid_token() -> None:
    create_response = client.post(
        "/api/todos",
        json={"title": "Protected todo"},
    )

    created_todo = create_response.json()

    get_response = client.get(
        f"/api/todos/{created_todo['id']}",
        headers={"Authorization": "Bearer test-token"},
    )

    assert get_response.status_code == 200
    assert get_response.json() == created_todo


@pytest.mark.local_api
def test_get_todo_returns_service_unavailable_without_token_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TODO_API_TOKEN")

    response = client.get(
        "/api/todos/1",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Authentication is not configured."


@pytest.mark.local_api
def test_openapi_documents_protected_todo_contract() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi_schema = response.json()
    get_todo_operation = openapi_schema["paths"]["/api/todos/{todo_id}"]["get"]

    documented_status_codes = set(
        get_todo_operation["responses"],
    )

    assert {
        "200",
        "401",
        "403",
        "404",
        "422",
        "503",
    }.issubset(documented_status_codes)

    authorization_parameter = next(
        parameter
        for parameter in get_todo_operation["parameters"]
        if parameter["name"] == "authorization"
    )

    assert authorization_parameter["in"] == "header"

    for status_code in ("401", "403", "404", "503"):
        response_schema = get_todo_operation["responses"][status_code]["content"][
            "application/json"
        ]["schema"]

    assert response_schema == {
        "$ref": "#/components/schemas/ErrorResponse",
    }
