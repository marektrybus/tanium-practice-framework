import pytest
from fastapi.testclient import TestClient

from app.main import app, todos

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_todos() -> None:
    todos.clear()

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
    ids=[
        "empty",
        "whitespace-only",
        "too-long"
    ]
    
)
def test_create_todo_rejects_invalid_title(
        invalid_title: str
    ) -> None:

    response = client.post(
        "/api/todos",
        json={"title": invalid_title},
    )

    assert response.status_code == 422


@pytest.mark.local_api
def test_create_todo_strips_surrounding_whitespace() -> None:
    response = client.post(
        "/api/todos",
        json={"title": "   sdf   "}
    )

    assert response.status_code == 201
    assert response.json()["title"] == "sdf"

@pytest.mark.local_api
def test_delete_existing_todo_removes_it() -> None:
    create_response = client.post(
        "/api/todos",
        json={"title": "todo to be deleted"}
    )

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