import time

import pytest
from playwright.sync_api import sync_playwright


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 15000) -> dict:
    deadline = time.time() + (timeout_ms / 1000.0)
    last = None
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return last
        page.wait_for_timeout(100)
    raise AssertionError(f"Expected last call path {expected_path}, got {last}")


@pytest.fixture(scope="session")
def docs_server() -> str:
    import os, subprocess, sys, socket
    from contextlib import closing
    def _is_open(host, port):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.2); return s.connect_ex((host, port)) == 0
    host, port = "127.0.0.1", 8777
    if not _is_open(host, port):
        proc = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def test_cm_p2s_works(docs_server: str):
    url = docs_server + "/translator_cm.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        # Seed minimal input and ensure op is prompt-to-spec
        page.select_option("#op", "p2s")
        try:
            page.locator("#cmIn .cm-content").wait_for(timeout=2000)
        except Exception:
            pass
        if page.locator("#cmIn .cm-content").count() > 0:
            page.click("#cmIn .cm-content")
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            page.keyboard.type("If a payment is approved then the order is shipped.", delay=1)
        else:
            page.fill("#inFallback", "If a payment is approved then the order is shipped.")
        # Click Translate and assert endpoint
        page.click("#run")
        _wait_last_call_path(page, "/llm/prompt-to-spec")
        # Copy out should work
        page.click("#copyOut")
        browser.close()


