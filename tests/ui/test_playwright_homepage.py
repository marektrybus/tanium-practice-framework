import re

import pytest
from playwright.sync_api import Page, expect


@pytest.mark.ui
def test_palywright_homepage_has_expected_title_and_link(page: Page) -> None:
    page.goto("https://playwright.dev/")

    expect(page).to_have_title(re.compile("Playwright"))
    expect(page.get_by_role("link", name="Get started")).to_be_visible()