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

    return f"""
    <!doctype html>
    <html lang="en">
      <head>
        <title>Local Todos</title>
      </head>
      <body>
        <h1>Local Todos</h1>
        <ul>{todo_items}</ul>
      </body>
    </html>
    """

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