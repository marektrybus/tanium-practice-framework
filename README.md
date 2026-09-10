# Tanium Practice Framework

An educational project for learning test automation in Python. It includes
unit, API, UI, and end-to-end integration tests built with `pytest`, FastAPI,
`requests`, and Playwright.

## Prerequisites

- Python 3.11 or newer
- Chromium for Playwright (installed by the command below)

## Local setup

Create and activate a virtual environment in the project directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m playwright install chromium
```

Verify that the terminal is using the interpreter from the current project:

```bash
which python
```

The output should point to `.venv/bin/python` within this project.

## Project structure

```text
app/        Local FastAPI Todo application
api/        REST API clients
config/     Environment-variable configuration
pages/      Page Objects for UI tests
utils/      Shared response validators and helpers
tests/      Test scenarios and pytest fixtures
```

## Code quality

Run the linter:

```bash
ruff check .
```

Automatically fix import formatting:

```bash
ruff check . --fix
```

## Running tests

Prefer `python -m pytest`. It guarantees that pytest is run by the Python
interpreter from the active `.venv` environment.

Run the full test suite:

```bash
python -m pytest -v
```

Run only unit tests, without network or browser dependencies:

```bash
python -m pytest -m unit -v
```

Run only API tests:

```bash
python -m pytest -m api -v
```

Run tests for the local FastAPI Todo API. The application runs in-process
through FastAPI's `TestClient`:

```bash
python -m pytest -m local_api -v
```

Run only UI tests:

```bash
python -m pytest -m ui -v
```

Run integration tests. These start the local FastAPI application, create a
todo through its REST API, and verify the same todo in the browser:

```bash
python -m pytest -m integration -v
```

Run one test file:

```bash
python -m pytest tests/ui/test_todos.py -v
```

Run one test:

```bash
python -m pytest tests/ui/test_todos.py::test_user_can_delete_a_todo -v
```

Available markers:

- `unit` — isolated tests without network access.
- `api` — tests requiring the external JSONPlaceholder API.
- `local_api` — tests of the locally owned FastAPI Todo API.
- `ui` — browser-based Playwright tests.
- `integration` — tests that cross API, application, and UI layers.

## Playwright: observing and debugging UI tests

Playwright runs the browser in the background (`headless`) by default. To see
the Chromium window:

```bash
python -m pytest -m ui -v --headed
```

To slow every Playwright action down by one second:

```bash
python -m pytest -m ui -v --headed --slowmo 1000
```

The `--slowmo` value is specified in milliseconds. For example, `500` means a
half-second delay between actions.

The same options can be used to observe the integration test locally:

```bash
python -m pytest -m integration -v --headed --slowmo 1000
```

To launch Playwright Inspector and step through actions:

```bash
PWDEBUG=1 python -m pytest tests/ui/test_todos.py::test_user_can_delete_a_todo -s
```

You can temporarily pause a test at a chosen point:

```python
todo_page.page.pause()
```

Remove `page.pause()` before committing the code.

## UI failure artifacts

Keep a trace and screenshot only for failed tests:

```bash
python -m pytest -m ui -v \
  --tracing retain-on-failure \
  --screenshot only-on-failure \
  --output test-results
```

`test-results/` contains local diagnostic artifacts and should not be committed
to Git. To inspect a local trace, use the path to its `.zip` file under
`test-results/`:

```bash
python -m playwright show-trace test-results/<path-to-trace.zip>
```

## API configuration

Override the API base URL in the current terminal session:

```bash
export API_BASE_URL="https://jsonplaceholder.typicode.com"
```

The client also supports a Bearer token through `API_TOKEN`. Never save real
tokens in source code, `pyproject.toml`, or the repository:

```bash
export API_TOKEN="your-local-token"
```

In production CI, secrets should come from a secure secrets store.
