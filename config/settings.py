import os

DEFAULT_API_BASE_URL = "https://jsonplaceholder.typicode.com"


def get_api_base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL).rstrip("/")


def get_api_token() -> str | None:
    return os.getenv("API_TOKEN")