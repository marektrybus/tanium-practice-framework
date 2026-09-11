from html import escape

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Local Todo Application")

todos: dict[int, "Todo"] = {}
next_todo_id = 1

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)

class Todo(BaseModel):
    id: int
    title: str

@app.get("/", response_class=HTMLResponse)
def todo_page() -> str:
    todo_items = "\n".join(
         f'<li data-testid="todo-item">{escape(todo.title)}</li>'
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

              button.addEventListener("click", async () => {
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

                const todoItem = document.createElement("li");
                todoItem.dataset.testid = "todo-item";
                todoItem.textContent = todo.title;
                todoList.appendChild(todoItem);
                input.value = "";
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



@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int) -> Response:
    if todo_id not in todos:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    del todos[todo_id]

    return Response(status_code=status.HTTP_204_NO_CONTENT)