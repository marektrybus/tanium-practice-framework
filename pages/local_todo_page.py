from playwright.sync_api import Locator, Page


class LocalTodoPage:
    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")
        self.todo_items = page.get_by_test_id("todo-item")

    def open(self) -> None:
        self.page.goto(self.base_url)

    def todo_with_text(self, todo_text: str) -> Locator:
        return self.todo_items.filter(has_text=todo_text)
