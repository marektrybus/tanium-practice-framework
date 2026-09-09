import requests
from requests import Response


class JsonPlaceholderClient:
    def __init__(self, base_url: str, token: str | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

        if token:
            self.session.headers.update(
                {"Authorization": f"Bearer {token}"}
            )

    def get_user(self, user_id: int) -> Response:
        return self.session.get(
            url=f"{self.base_url}/users/{user_id}",
            timeout=10,
        )

    def close(self) -> None:
        self.session.close()