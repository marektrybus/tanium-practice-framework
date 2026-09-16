import os
import socket
import subprocess
import sys
import time
from collections.abc import Iterator

import pytest
import requests
from playwright.sync_api import Page

from api.jsonplaceholder_client import JsonPlaceholderClient
from api.local_todo_client import LocalTodoClient
from config.settings import get_api_base_url, get_api_token
from pages.local_todo_page import LocalTodoPage
from pages.todo_page import TodoPage


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return get_api_base_url()

@pytest.fixture
def api_client(api_base_url: str) -> Iterator[JsonPlaceholderClient]:
    client = JsonPlaceholderClient(
        base_url=api_base_url,
        token=get_api_token(),
        )

    yield client

    client.close()

@pytest.fixture
def todo_page(page: Page) -> TodoPage:
    todo_page = TodoPage(page)
    todo_page.open()

    return todo_page

@pytest.fixture
def local_app_url(
    local_todo_api_token: str,
    ) -> Iterator[str]:
    with socket.socket() as socket_server:
        socket_server.bind(("127.0.0.1", 0))
        port = socket_server.getsockname()[1]

    base_url = f"http://127.0.0.1:{port}"
    process_environment = os.environ.copy()
    process_environment["TODO_API_TOKEN"] = local_todo_api_token
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=process_environment,
    )

    for _ in range(50):
        try:
            requests.get(f"{base_url}/openapi.json", timeout=0.2)
            break
        except requests.ConnectionError:
            time.sleep(0.1)
    else:
        process.terminate()
        raise RuntimeError("Local FastAPI server did not start.")

    yield base_url

    process.terminate()
    process.wait()

@pytest.fixture
def local_todo_api_token() -> str:
    return "integration-test-token"

@pytest.fixture
def local_todo_client(
    local_app_url: str,
    local_todo_api_token: str,
) -> Iterator[LocalTodoClient]:
    client = LocalTodoClient(
        local_app_url,
        token=local_todo_api_token,
    )

    yield client

    client.close()

@pytest.fixture
def local_todo_page(
    page: Page,
    local_app_url: str,
) -> LocalTodoPage:
    return LocalTodoPage(page, local_app_url)

@pytest.fixture
def unauthenticated_local_todo_client(
    local_app_url: str,
) -> Iterator[LocalTodoClient]:
    client = LocalTodoClient(local_app_url)

    yield client

    client.close()