import time

from playwright.sync_api import sync_playwright
from tests.e2e.ui.test_translator_live import docs_server as _docs_server_fixture


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 15000) -> dict:
    deadline = time.time() + (timeout_ms / 1000.0)
    last = None
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return last
        page.wait_for_timeout(100)
    raise AssertionError(f"Expected last call path {expected_path}, got {last}")


def test_ui_assist_chat_send(_docs_server_fixture):
    base = _docs_server_fixture
    url = base + "/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        # Open Assist
        page.click("#toggleChat")
        page.wait_for_selector("#chatDrawer")
        # Type and send
        page.fill("#chatInput", "Explain: always (a -> b)")
        page.click("#chatSend")
        # Wait for the last-call oracle to be set by the generic post() helper
        _wait_last_call_path(page, "/llm/chat")
        browser.close()


