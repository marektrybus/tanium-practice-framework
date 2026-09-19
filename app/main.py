import os
from html import escape

from fastapi import Depends, FastAPI, Header, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(title="Local Todo Application")

todos: dict[int, "Todo"] = {}
next_todo_id = 1


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, title: str) -> str:
        normalized_title = title.strip()

        if not normalized_title:
            raise ValueError("Title must not be blank.")

        return normalized_title


class Todo(BaseModel):
    id: int
    title: str


class ErrorResponse(BaseModel):
    detail: str


def require_todo_api_token(
    authorization: str | None = Header(default=None),
) -> None:
    expected_token = os.getenv("TODO_API_TOKEN")

    if expected_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured.",
        )

    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    scheme, _, provided_token = authorization.partition(" ")

    if scheme != "Bearer" or provided_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API token.",
        )


@app.get("/", response_class=HTMLResponse)
def todo_page() -> str:
    todo_items = "\n".join(
        f"""
        <li data-testid="todo-item" data-todo-id="{todo.id}">
          <span>{escape(todo.title)}</span>
          <button
            type="button"
            data-testid="delete-todo"
            aria-label="Delete"
          >
            Delete
          </button>
        </li>
        """
        for todo in todos.values()
    )

    return (
        """<!doctype html>
        <html lang="en">
          <head>
            <title>Local Todos</title>
          </head>
          <body>
            <h1>Local Todos</h1>

            <input
              data-testid="new-todo-input"
              placeholder="What needs to be done?"
            />
            <button data-testid="add-todo">Add todo</button>
            <p
              data-testid="error-message"
              role="alert"
              hidden
            ></p>

            <ul data-testid="todo-list">"""
        + todo_items
        + """</ul>

            <script>
              const input = document.querySelector(
                '[data-testid="new-todo-input"]',
              );
              const button = document.querySelector(
                '[data-testid="add-todo"]',
              );
              const todoList = document.querySelector(
                '[data-testid="todo-list"]',
              );

              const errorMessage = document.querySelector(
                '[data-testid="error-message"]',
              );

              function showError(message) {
                errorMessage.textContent = message;
                errorMessage.hidden = false;
              }

              function clearError() {
                errorMessage.textContent = "";
                errorMessage.hidden = true;
              }

              function appendTodo(todo) {
                const todoItem = document.createElement("li");
                todoItem.dataset.testid = "todo-item";
                todoItem.dataset.todoId = todo.id;

                const todoText = document.createElement("span");
                todoText.textContent = todo.title;

                const deleteButton = document.createElement("button");
                deleteButton.type = "button";
                deleteButton.dataset.testid = "delete-todo";
                deleteButton.setAttribute("aria-label", "Delete");
                deleteButton.textContent = "Delete";

                todoItem.append(todoText, deleteButton);
                todoList.appendChild(todoItem);
              }

              button.addEventListener("click", async () => {
                clearError();

                const title = input.value.trim();

                if (!title) {
                  return;
                }

                const response = await fetch("/api/todos", {
                  method: "POST",
                  headers: {"Content-Type": "application/json"},
                  body: JSON.stringify({title}),
                });
                const todo = await response.json();

                appendTodo(todo);
                input.value = "";
              });

              todoList.addEventListener("click", async (event) => {
                const deleteButton = event.target.closest(
                  '[data-testid="delete-todo"]',
                );

                if (!deleteButton) {
                  return;
                }

                const todoItem = deleteButton.closest(
                  '[data-testid="todo-item"]',
                );

                if (!todoItem) {
                  return;
                }

                const todoId = todoItem.dataset.todoId;
                const response = await fetch(`/api/todos/${todoId}`, {
                  method: "DELETE",
                });

                if (response.status === 204) {
                  todoItem.remove();
                  return;
                }

                showError("Could not delete todo. Please try again.");
              });
            </script>
          </body>
        </html>"""
    )


@app.get("/api/todos", response_model=list[Todo])
def get_todos() -> list[Todo]:
    return list(todos.values())


@app.post(
    "/api/todos",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
)
def create_todo(payload: TodoCreate) -> Todo:
    global next_todo_id

    todo = Todo(id=next_todo_id, title=payload.title)
    todos[todo.id] = todo
    next_todo_id += 1

    return todo


@app.get(
    "/api/todos/{todo_id}",
    response_model=Todo,
    dependencies=[Depends(require_todo_api_token)],
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Authorization header is required.",
        },
        403: {
            "model": ErrorResponse,
            "description": "The Bearer token is invalid.",
        },
        404: {
            "model": ErrorResponse,
            "description": "The requested todo does not exist.",
        },
        503: {
            "model": ErrorResponse,
            "description": "Authentication is not configured.",
        },
    },
)
def get_todo(todo_id: int) -> Todo:
    if todo_id not in todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return todos[todo_id]


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> Response:
    if todo_id not in todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    del todos[todo_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)
