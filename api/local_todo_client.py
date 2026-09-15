import requests
from requests import Response


class LocalTodoClient:
    def __init__(
        self,
        base_url: str,
        token: str | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        if token:
            self.session.headers.update(
                {"Authorization": f"Bearer {token}"},
            )

    def create_todo(self, title: str) -> Response:
        return self.session.post(
            f"{self.base_url}/api/todos",
            json={"title": title},
            timeout=10,
        )

    def get_todos(self) -> Response:
        return self.session.get(
            f"{self.base_url}/api/todos",
            timeout=10,
        )

    def get_todo(self, todo_id: int) -> Response:
        return self.session.get(
            f"{self.base_url}/api/todos/{todo_id}",
            timeout=10,
        )
    