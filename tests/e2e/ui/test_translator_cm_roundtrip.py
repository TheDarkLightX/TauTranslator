import time

import pytest
from playwright.sync_api import sync_playwright, expect


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
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _cm_set_text(page, text: str) -> None:
    # Prefer CM6 content if present; otherwise fallback textarea
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


def _get_output_text(page) -> str:
    # Prefer backing stores when available
    val = page.evaluate("() => (document.getElementById('outTau')?.value||'') + (document.getElementById('outTce')?.value||'') + (document.getElementById('outExplanation')?.value||'') + (document.getElementById('outModule')?.value||'')")
    if val:
        return val
    # Fallback to visible editor/textarea
    vis_cm = page.evaluate("() => getComputedStyle(document.getElementById('cmOut')).display !== 'none'")
    if vis_cm:
        return page.inner_text("#cmOut .cm-content")
    return page.eval_on_selector("#outFallback", "el => el.value || ''")


def _wait_any_output(page, timeout_ms: int = 15000) -> None:
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
        page.wait_for_timeout(100)
    raise AssertionError("Timed out waiting for any output text")


def _wait_validate_output(page, timeout_ms: int = 15000) -> None:
    deadline = time.time() + (timeout_ms / 1000.0)
    cm_out = page.locator("#cmOut .cm-content")
    fallback = page.locator("#outFallback")
    while time.time() < deadline:
        try:
            if cm_out.count() and (cm_out.inner_text().strip() if cm_out.inner_text() else ""):
                return
            if fallback.count() and fallback.input_value().strip():
                return
        except Exception:
            pass
        page.wait_for_timeout(100)
    raise AssertionError("Timed out waiting for validate output")


def test_cm_p2s_basic_roundtrip(docs_server: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(docs_server + "/translator_cm.html", wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        # p2s
        page.select_option("#op", "p2s")
        _cm_set_text(page, "If a payment is approved then the order is shipped.")
        page.click("#run")
        _wait_last_call_path(page, "/llm/prompt-to-spec")
        _wait_any_output(page)
        out = _get_output_text(page)
        assert "always" in out or "order" in out
        # s2p on produced Tau
        tau = page.evaluate("() => document.getElementById('outTau').value || ''")
        assert tau
        page.select_option("#op", "s2p")
        _cm_set_text(page, tau)
        page.click("#run")
        _wait_last_call_path(page, "/llm/spec-to-prompt")
        _wait_any_output(page)
        expl = page.evaluate("() => document.getElementById('outExplanation').value || ''")
        if not expl:
            try:
                expl = page.inner_text("#cmOut .cm-content").strip()
            except Exception:
                expl = page.eval_on_selector("#outFallback", "el => el.value || ''")
        assert expl and ("if" in expl.lower() or "then" in expl.lower())
        browser.close()


def test_cm_validate_and_tce2tau(docs_server: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(docs_server + "/translator_cm.html", wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        # validate
        page.select_option("#op", "validate")
        _cm_set_text(page, "always (temperature_high -> fan_on)")
        page.click("#run")
        _wait_last_call_path(page, "/validate/tce")
        _wait_validate_output(page)
        txt = _get_output_text(page)
        assert "Valid" in txt or "Invalid" in txt
        # tce2tau
        page.select_option("#op", "tce2tau")
        _cm_set_text(page, "If a payment is approved then the order is shipped.")
        page.click("#run")
        _wait_last_call_path(page, "/translate/tce-to-tau")
        _wait_any_output(page)
        tau = page.evaluate("() => document.getElementById('outTau').value || ''")
        assert tau and "always" in tau
        browser.close()


def test_cm_tau_time_index_explain(docs_server: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(docs_server + "/translator_cm.html", wait_until="domcontentloaded")
        page.wait_for_timeout(400)
        page.select_option("#op", "s2p")
        tau = "always ((i1[t] != 1) -> (o1[t] != 0))"
        _cm_set_text(page, tau)
        page.click("#run")
        _wait_last_call_path(page, "/llm/spec-to-prompt")
        _wait_any_output(page)
        expl = page.evaluate("() => document.getElementById('outExplanation').value || ''")
        assert expl
        browser.close()


