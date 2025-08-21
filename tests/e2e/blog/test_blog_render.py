import os
import socket
import subprocess
import sys
import time
from contextlib import closing

import pytest
from playwright.sync_api import sync_playwright


def _is_port_open(host: str, port: int) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex((host, port)) == 0


def _wait_for_server(host: str, port: int, timeout_s: float = 10.0) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        if _is_port_open(host, port):
            return
        time.sleep(0.05)
    raise TimeoutError(f"Server did not start on {host}:{port} within {timeout_s}s")


@pytest.fixture(scope="session")
def docs_server() -> str:
    """Start a local HTTP server rooted at ./docs and yield base URL."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    docs_dir = os.path.join(repo_root, "docs")
    assert os.path.isdir(docs_dir), f"docs directory not found: {docs_dir}"

    host = "127.0.0.1"
    port = 8765
    env = os.environ.copy()
    # Use the test runner's Python to avoid venv mismatch
    python_exec = sys.executable
    # Start http.server serving docs as root
    proc = subprocess.Popen(
        [python_exec, "-m", "http.server", str(port), "--directory", docs_dir],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=repo_root,
        env=env,
    )
    try:
        _wait_for_server(host, port, timeout_s=15.0)
        yield f"http://{host}:{port}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def _collect_page_issues(page):
    errors = []
    fails = []

    def on_console(msg):
        if msg.type == "error":
            errors.append((msg.type, msg.text))

    def on_failed(request):
        fails.append((request.url, request.failure))

    page.on("console", on_console)
    page.on("requestfailed", on_failed)
    return errors, fails


def test_pancomputationalism_renders_katex_and_no_errors(docs_server):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            errors, fails = _collect_page_issues(page)
            page.goto(docs_server + "/blog/pancomputationalism.html", wait_until="load")
            # Wait for KaTeX render to attach spans
            page.wait_for_selector(".math-block .katex, span.katex", timeout=10000)

            # No console errors
            assert not errors, f"Console errors: {errors}"
            # No failed network requests (CDN/css/js)
            assert not fails, f"Failed requests: {fails}"
        finally:
            browser.close()


@pytest.mark.parametrize("path", [
    "/blog/index.html",
    "/blog/undecidability-consciousness.html",
])
def test_blog_pages_no_console_or_network_errors(docs_server, path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            errors, fails = _collect_page_issues(page)
            page.goto(docs_server + path, wait_until="load")
            # Allow late script loads
            page.wait_for_timeout(500)
            assert not errors, f"Console errors on {path}: {errors}"
            assert not fails, f"Failed requests on {path}: {fails}"
        finally:
            browser.close()


