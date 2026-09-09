from playwright.sync_api import Locator, Page


class TodoPage:
    URL = "https://demo.playwright.dev/todomvc/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.new_todo_input = page.get_by_placeholder(
            "What needs to be done?",
        )
        self.todo_items = page.get_by_test_id("todo-item")

    def open(self) -> None:
        self.page.goto(self.URL)

    def add_todo(self, todo_text: str) -> None:
        self.new_todo_input.fill(todo_text)
        self.new_todo_input.press("Enter")

    def todo_with_text(self, todo_text: str) -> Locator:
        return self.todo_items.filter(has_text=todo_text)

    def delete_todo(self, todo_text: str) -> None:
        todo_to_delete = self.todo_with_text(todo_text)
        todo_to_delete.hover()
        todo_to_delete.get_by_label("Delete").click()