import random
import time
import socket
import subprocess
import sys
from contextlib import closing

import pytest
from playwright.sync_api import sync_playwright


def _is_open(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def docs_server() -> str:
    host, port = "127.0.0.1", 8777
    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _rand_prompt(rng: random.Random) -> str:
    subjects = ["payment", "order", "sensor", "user", "session"]
    verbs = ["approved", "shipped", "high", "logged in", "exists"]
    s = rng.choice(subjects)
    v = rng.choice(verbs)
    return f"If a {s} is {v} then proceed."  # natural-language p2s


def _rand_tau(rng: random.Random) -> str:
    atoms = ["a", "b", "c", "p", "q"]
    a, b = rng.choice(atoms), rng.choice(atoms)
    forms = [
        f"always ({a} -> {b})",
        f"always ({a} && {b})",
        f"always (!{a})",
    ]
    return rng.choice(forms)


def _cm_set_text(page, text: str) -> None:
    try:
        page.locator("#cmIn .cm-content").wait_for(timeout=2000)
    except Exception:
        pass
    if page.locator("#cmIn .cm-content").count() > 0:
        page.click("#cmIn .cm-content")
        page.keyboard.press("Control+A")
        page.keyboard.press("Backspace")
        if text:
            page.keyboard.type(text, delay=1)
    else:
        page.fill("#inFallback", text)


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 10000) -> None:
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"Expected last call path {expected_path}")


def test_ui_fuzz_current_cm6(docs_server: str):
    url = docs_server + "/translator_cm.html"
    rng = random.Random(42)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        # Ensure privacy mode off for network attempts; but tests rely on oracle, not responses
        page.evaluate("() => localStorage.setItem('tau_privacy_mode','0')")
        # Run a small fuzz corpus
        for i in range(6):
            op = rng.choice(["p2s", "validate", "tce2tau", "s2p"])  # operations
            page.select_option("#op", op)
            if op == "p2s":
                _cm_set_text(page, _rand_prompt(rng))
                page.click("#run")
                _wait_last_call_path(page, "/llm/prompt-to-spec")
            elif op == "validate":
                _cm_set_text(page, _rand_tau(rng))
                page.click("#run")
                _wait_last_call_path(page, "/validate/tce")
            elif op == "tce2tau":
                _cm_set_text(page, _rand_prompt(rng))
                page.click("#run")
                _wait_last_call_path(page, "/translate/tce-to-tau")
            else:  # s2p
                _cm_set_text(page, _rand_tau(rng))
                page.click("#run")
                _wait_last_call_path(page, "/llm/spec-to-prompt")
        browser.close()


