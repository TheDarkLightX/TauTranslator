import os
import time
import pytest
from playwright.sync_api import sync_playwright


@pytest.mark.skipif(not os.environ.get('OPENROUTER_KEY'), reason="OPENROUTER_KEY env var required for BYOK E2E")
def test_cm6_chat_byok(docs_server: str = None):
    # Use provided docs_server pattern from other tests if not passed
    if not docs_server:
        host, port = "127.0.0.1", 8777
        import socket, subprocess, sys
        from contextlib import closing
        def _is_open(h, p):
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
                s.settimeout(0.2); return s.connect_ex((h, p)) == 0
        if not _is_open(host, port):
            subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
            time.sleep(1.0)
        docs_server = f"http://{host}:{port}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Pass BYOK via URL to auto-save into localStorage and prefill field
        byok = os.environ["OPENROUTER_KEY"]
        page.goto(docs_server + f"/translator_cm.html?api=https://tau-translator-api.fly.dev&byok={byok}", wait_until="domcontentloaded")
        page.wait_for_timeout(300)
        # Ensure privacy mode is off
        page.evaluate("() => { localStorage.setItem('tau_privacy_mode','0'); }")
        # Open chat and send a ping
        page.click('#toggleChat')
        page.fill('#chatInput', 'ping: please reply with "pong"')
        page.click('#chatSend')
        # Verify BYOK header was set for /llm/chat
        deadline_meta = time.time() + 5
        meta = None
        while time.time() < deadline_meta:
            meta = page.evaluate("() => window.__tau_last_call || null")
            if isinstance(meta, dict) and meta.get('path') == '/llm/chat':
                break
            page.wait_for_timeout(100)
        assert meta and meta.get('path') == '/llm/chat'
        headers = meta.get('headers') or {}
        assert headers.get('X-OpenRouter-Key'), 'BYOK header missing'
        # Wait for assistant message
        deadline = time.time() + 25
        got = ''
        while time.time() < deadline:
            got = page.inner_text('#chatMessages')
            if 'assistant' in got.lower() and ('pong' in got.lower() or 'reply' in got.lower() or len(got.strip()) > 10):
                break
            page.wait_for_timeout(250)
        assert 'assistant' in got.lower() and len(got.strip()) > 10
        browser.close()


