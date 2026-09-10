import requests
from requests import Response


class LocalTodoClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def create_todo(self, title: str) -> Response:
        return requests.post(
            f"{self.base_url}/api/todos",
            json={"title": title},
            timeout=10,
        )