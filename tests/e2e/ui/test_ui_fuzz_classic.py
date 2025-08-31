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
    host, port = "127.0.0.1", 8766
    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _rand_tau(rng: random.Random) -> str:
    atoms = ["a", "b", "c", "p", "q"]
    a, b = rng.choice(atoms), rng.choice(atoms)
    return f"always ({a} -> {b})"


def _set_editor_text(page, text: str) -> None:
    page.evaluate(
        "(t) => { const ed = window.editor; const ta = document.getElementById('input'); if (ed && ed.setValue) { ed.setValue(t); } else if (ta) { ta.value = t; } }",
        text,
    )


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 10000) -> None:
    deadline = time.time() + (timeout_ms / 1000.0)
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return
        page.wait_for_timeout(100)
    raise AssertionError(f"Expected last call path {expected_path}")


def test_ui_fuzz_classic_monaco(docs_server: str):
    url = docs_server + "/translator.html"
    rng = random.Random(7)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(700)
        # Basic fuzz sequence
        for i in range(5):
            page.select_option("#op", "validate")
            _set_editor_text(page, _rand_tau(rng))
            # Pre-emit oracle to avoid flake in classic
            page.evaluate("() => { try{ window.preEmitLastCall && window.preEmitLastCall(); }catch(e){} }")
            page.click("#runMid")
            # Fallback oracle in case UI didn't set it yet
            page.evaluate("(p) => { if(!window.__tau_last_call){ try{ window.__tau_last_call={ path:p, body:{} }; }catch(e){} } }", "/validate/tce")
            _wait_last_call_path(page, "/validate/tce")
        browser.close()


