import pytest
from playwright.sync_api import expect

from pages.todo_page import TodoPage


@pytest.mark.ui
def test_user_can_add_a_todo(todo_page: TodoPage) -> None:
    todo_text = "Prepare for Tanium onboarding"

    todo_page.add_todo(todo_text)

    todo_item = todo_page.todo_with_text(todo_text)

    expect(todo_item).to_have_count(1)
    expect(todo_item).to_be_visible()

@pytest.mark.ui
def test_user_can_delete_a_todo(todo_page: TodoPage) -> None:
    todo_text = "todo to delete"
    todo_page.add_todo(todo_text)

    todo_page.delete_todo(todo_text)

    expect(todo_page.todo_with_text(todo_text)).to_have_count(0)