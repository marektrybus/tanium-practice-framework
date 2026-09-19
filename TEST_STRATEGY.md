# Test Strategy

## Purpose

This project demonstrates a layered Python test automation framework for API,
UI, and integration testing.

The goal is to detect defects as close to their source as practical while
keeping feedback fast and actionable.

## Test layers

| Layer | Marker | Scope | Examples |
|---|---|---|---|
| Unit | `unit` | Isolated Python logic with mocked dependencies | Response validation, settings, API client request construction |
| External API | `api` | Real requests to JSONPlaceholder | User response validation |
| Local API | `local_api` | FastAPI application through `TestClient` | Validation, authentication, status codes, OpenAPI contract |
| UI | `ui` | Browser scenarios against TodoMVC | Add and delete todos |
| Integration | `integration` | Local Uvicorn server, `requests`, FastAPI, and Playwright | API-to-UI flow, UI-to-API flow, authentication |

## Test data and isolation

- Local API tests clear in-memory todos before each test.
- Integration tests start a separate local Uvicorn process per test.
- Each integration test receives a dedicated local server URL and test token.
- HTTP sessions are closed in fixture teardown.
- External API tests use read-only endpoints and do not create shared data.

## API contract coverage

The protected `GET /api/todos/{todo_id}` endpoint verifies:

- missing Authorization header returns `401`;
- invalid Bearer token returns `403`;
- missing todo with a valid token returns `404`;
- missing server-side token configuration returns `503`;
- valid credentials return `200` and a Todo response;
- `/openapi.json` documents status codes, header requirements, and error schemas.

## UI coverage

UI tests use Page Objects and user-facing locators. They verify:

- a user can add a todo;
- a user can delete a todo;
- data created through the API is visible in the UI;
- data created through the UI is available through the API;
- a simulated API failure keeps the todo visible and shows an error message.

## CI strategy

GitHub Actions runs separate jobs for:

- code quality and unit tests;
- external API tests;
- local API tests;
- UI tests;
- integration tests.

UI and integration jobs retain Playwright traces and screenshots only when a
test fails.

## Quality gates

- `ruff check .` detects linting and import issues.
- `ruff format --check .` enforces consistent formatting.
- `--strict-markers` prevents unregistered pytest markers.
- Coverage measures both line and branch coverage for the project code.

## Known limitations

The local Todo application uses in-memory storage and a simple demonstration
Bearer token. A production system would normally use persistent storage,
centralized identity management, secret management, observability, and
environment-specific test data controls.