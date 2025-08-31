import time
import socket
import subprocess
import sys
from contextlib import closing

import pytest
from playwright.sync_api import sync_playwright, expect


def _is_open(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


@pytest.fixture(scope="session")
def docs_server_cm() -> str:
    host, port = "127.0.0.1", 8777
    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


@pytest.fixture(scope="session")
def docs_server_classic() -> str:
    host, port = "127.0.0.1", 8766
    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def test_cm6_online_api_connects(docs_server_cm: str):
    url = docs_server_cm + "/translator_cm.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(300)
        # Point to official API and test connectivity
        page.fill('#apiBase', 'https://tau-translator-api.fly.dev')
        page.click('#testApi')
        expect(page.locator('#apiStatus')).to_have_text('online', timeout=5000)
        # Run p2s and assert last call uses remote URL and no offline fallback for LLM path
        page.select_option('#op', 'p2s')
        page.fill('#inFallback', 'If a payment is approved then the order is shipped.')
        page.click('#run')
        deadline = time.time() + 10
        got_llm = False
        while time.time() < deadline:
            meta = page.evaluate("() => window.__tau_last_call || null")
            if isinstance(meta, dict) and meta.get('path') == '/llm/prompt-to-spec' and 'tau-translator-api.fly.dev' in (meta.get('url') or ''):
                got_llm = True
                break
            page.wait_for_timeout(100)
        assert got_llm, 'p2s did not hit remote API'
        reasons = page.inner_text('#reasons') if page.locator('#reasons').count() else ''
        assert 'Offline' not in reasons and 'Network error' not in reasons
        browser.close()


def test_classic_online_validate_connects(docs_server_classic: str):
    url = docs_server_classic + "/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        # Ensure API base
        page.fill('#apiBase', 'https://tau-translator-api.fly.dev')
        # Validate path (deterministic)
        page.select_option('#op', 'validate')
        page.evaluate("() => { const ta=document.getElementById('input'); if(ta){ ta.value='always (a -> b)'; } }")
        # Pre-emit and trigger both runMid and main run for robustness
        page.evaluate("() => { try{ window.preEmitLastCall && window.preEmitLastCall(); }catch(e){} }")
        page.click('#runMid')
        page.evaluate("() => { const b=document.getElementById('run'); if(b && !b.disabled){ b.click(); } }")
        # Assert last call url
        deadline = time.time() + 10
        got_val = False
        while time.time() < deadline:
            meta = page.evaluate("() => window.__tau_last_call || null")
            if isinstance(meta, dict) and meta.get('path') == '/validate/tce' and 'tau-translator-api.fly.dev' in (meta.get('url') or ''):
                got_val = True
                break
            page.wait_for_timeout(100)
        assert got_val, 'validate did not hit remote API'
        browser.close()


