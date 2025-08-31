import os
import time
import pytest
from playwright.sync_api import sync_playwright


def _wait_last_call_path(page, expected_path: str, timeout_ms: int = 25000) -> dict:
    deadline = time.time() + (timeout_ms / 1000.0)
    last = None
    while time.time() < deadline:
        last = page.evaluate("() => window.__tau_last_call || null")
        if last and isinstance(last, dict) and last.get("path") == expected_path:
            return last
        page.wait_for_timeout(150)
    raise AssertionError(f"Expected last call path {expected_path}, got {last}")


def _cm_set_text(page, text: str) -> None:
    try:
        page.locator("#cmIn .cm-content").wait_for(timeout=3000)
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


def _wait_any_output(page, timeout_ms: int = 25000) -> None:
    deadline = time.time() + (timeout_ms / 1000.0)
    tau = page.locator("#outTau")
    tce = page.locator("#outTce")
    expl = page.locator("#outExplanation")
    module = page.locator("#outModule")
    cm_out = page.locator("#cmOut .cm-content")
    while time.time() < deadline:
        try:
            if tau.count() and tau.input_value().strip():
                return
            if tce.count() and tce.input_value().strip():
                return
            if expl.count() and expl.input_value().strip():
                return
            if module.count() and module.input_value().strip():
                return
            if cm_out.count() and (cm_out.inner_text().strip() if cm_out.inner_text() else ""):
                return
        except Exception:
            pass
        page.wait_for_timeout(150)
    raise AssertionError("Timed out waiting for any output text")


@pytest.mark.skipif(not os.environ.get('OPENROUTER_KEY'), reason="OPENROUTER_KEY env var required for BYOK E2E")
def test_byok_p2s_and_s2p_roundtrip():
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
        byok = os.environ["OPENROUTER_KEY"]
        # Use API prod and BYOK via URL for convenience
        page.goto(docs_server + f"/translator_cm.html?api=https://tau-translator-api.fly.dev&byok={byok}", wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        page.evaluate("() => { localStorage.setItem('tau_privacy_mode','0'); }")

        # 1) Prompt -> Spec using LLM
        page.select_option("#op", "p2s")
        _cm_set_text(page, "If a payment is approved then the order is shipped.")
        page.click("#run")
        meta = _wait_last_call_path(page, "/llm/prompt-to-spec")
        headers = meta.get('headers') or {}
        assert headers.get('X-OpenRouter-Key'), 'BYOK header missing for p2s'
        _wait_any_output(page)
        tau = page.evaluate("() => document.getElementById('outTau').value || ''")
        assert tau and ("always" in tau or "->" in tau or "order" in tau)

        # 2) Spec -> Prompt using LLM (quantifiers/negation/temporal indices included)
        page.select_option("#op", "s2p")
        _cm_set_text(page, tau)
        page.click("#run")
        meta2 = _wait_last_call_path(page, "/llm/spec-to-prompt")
        headers2 = meta2.get('headers') or {}
        assert headers2.get('X-OpenRouter-Key'), 'BYOK header missing for s2p'
        _wait_any_output(page)
        expl = page.evaluate("() => document.getElementById('outExplanation').value || ''")
        if not expl:
            try:
                expl = page.inner_text("#cmOut .cm-content").strip()
            except Exception:
                expl = page.eval_on_selector("#outFallback", "el => el.value || ''")
        assert expl and ("if" in expl.lower() or "then" in expl.lower())

        # 3) Quick assist background chat sanity with BYOK
        page.click('#toggleChat')
        page.fill('#chatInput', 'Given our spec, suggest one test case: respond tersely.')
        page.click('#chatSend')
        # Verify last call is llm/chat with BYOK
        deadline_meta = time.time() + 8
        meta3 = None
        while time.time() < deadline_meta:
            meta3 = page.evaluate("() => window.__tau_last_call || null")
            if isinstance(meta3, dict) and meta3.get('path') == '/llm/chat':
                break
            page.wait_for_timeout(100)
        assert meta3 and meta3.get('path') == '/llm/chat'
        headers3 = meta3.get('headers') or {}
        assert headers3.get('X-OpenRouter-Key'), 'BYOK header missing for chat'

        deadline = time.time() + 25
        got = ''
        while time.time() < deadline:
            got = page.inner_text('#chatMessages')
            if 'assistant' in got.lower() and len(got.strip()) > 10:
                break
            page.wait_for_timeout(250)
        assert 'assistant' in got.lower() and len(got.strip()) > 10

        # Close chat drawer so it doesn't intercept clicks over Translate
        try:
            page.click('#toggleChat')
            page.wait_for_timeout(150)
        except Exception:
            pass
        # Hard-close overlay if still open
        page.evaluate("() => { const el = document.getElementById('chatDrawer'); if (el) { el.classList.remove('is-open'); el.style.pointerEvents='none'; el.style.display='none'; } }")

        # 4) Additional p2s with quantifiers and negation to ensure breadth
        page.select_option("#op", "p2s")
        _cm_set_text(page, "For every user x, if x is logged in then there exists a session for x.")
        page.click("#run")
        meta_q = _wait_last_call_path(page, "/llm/prompt-to-spec")
        headers_q = meta_q.get('headers') or {}
        assert headers_q.get('X-OpenRouter-Key'), 'BYOK header missing for p2s quantifiers'
        _wait_any_output(page)
        tau_q = page.evaluate("() => document.getElementById('outTau').value || ''")
        assert tau_q and ("all" in tau_q or "ex" in tau_q or "->" in tau_q)

        # 5) Negative guard prompt
        page.select_option("#op", "p2s")
        _cm_set_text(page, "Never send data over the network.")
        page.click("#run")
        meta_neg = _wait_last_call_path(page, "/llm/prompt-to-spec")
        headers_neg = meta_neg.get('headers') or {}
        assert headers_neg.get('X-OpenRouter-Key'), 'BYOK header missing for p2s negation'
        _wait_any_output(page)
        tau_neg = page.evaluate("() => document.getElementById('outTau').value || ''")
        # LLM outputs vary; require structural Tau-like signal
        assert tau_neg and ("always (" in tau_neg) and any(tok in tau_neg for tok in ["!", "all", "->", "&&", "||"])

        browser.close()


