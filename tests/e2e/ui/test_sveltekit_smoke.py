import time
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def svelte_preview() -> str:
    import os, subprocess, sys, socket
    from contextlib import closing
    host, port = "127.0.0.1", 5199
    def _is_open(h,p):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.2)
            return s.connect_ex((h,p)) == 0
    env = os.environ.copy()
    if not _is_open(host, port):
        proc = subprocess.Popen(["npm", "run", "preview"], cwd="apps/sveltekit", env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 15000) -> dict:
    deadline = time.time() + (timeout_ms / 1000.0)
    last = None
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return last
        page.wait_for_timeout(100)
    raise AssertionError(f"Expected last call path {expected_path}, got {last}")


def test_sveltekit_translate_and_assist(svelte_preview: str):
    url = svelte_preview + "/"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        # Wait UI ready flag
        deadline = time.time() + 2000
        while time.time() < deadline:
            if page.evaluate("() => !!window.TAU_UI_READY"):
                break
            page.wait_for_timeout(50)
        # Translate
        page.wait_for_selector("#btnTranslate", timeout=3000)
        # Ensure input has default content
        page.wait_for_timeout(200)
        page.click("#btnTranslate")
        _wait_last_call_path(page, "/llm/prompt-to-spec")
        # Assist: open and send
        page.click("#btnAssist")
        page.fill("#assistInput", "Explain always (p -> q)")
        page.click("#assistSend")
        _wait_last_call_path(page, "/llm/chat")
        browser.close()


