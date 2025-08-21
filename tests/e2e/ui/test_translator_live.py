from __future__ import annotations

import re
import time
from urllib.parse import urlparse

import pytest
from playwright.sync_api import sync_playwright


def _collect(page):
    errors = []
    fails = []

    def on_console(msg):
        if msg.type == "error":
            errors.append((msg.type, msg.text))

    def on_failed(req):
        fails.append((req.url, req.failure))

    page.on("console", on_console)
    page.on("requestfailed", on_failed)
    return errors, fails


def test_live_translator_input_not_blocked():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            errors, fails = _collect(page)
            page.goto(url, wait_until="domcontentloaded")
            # Allow Monaco to load and drawers to settle
            page.wait_for_timeout(1200)

            # If Examples drawer opened by first-time nudge, close it to reduce overlap
            try:
                if page.is_visible("#examplesDrawer"):
                    # If drawer is open (left=0), close it
                    left = page.eval_on_selector("#examplesDrawer", "el => getComputedStyle(el).left")
                    if left and re.match(r"^0(px)?$", left.strip()):
                        page.click("#closeExamples")
                        page.wait_for_timeout(200)
            except Exception:
                pass

            # Verify an input surface exists: Monaco or fallback textarea (wait up to 5s)
            deadline = time.time() + 5.0
            has_monaco = False
            has_textarea = False
            while time.time() < deadline:
                has_monaco = page.query_selector("#editor .monaco-editor") is not None
                has_textarea = page.is_visible("#input")
                if has_monaco or has_textarea:
                    break
                page.wait_for_timeout(150)
            assert has_monaco or has_textarea, "No input editor nor fallback textarea visible after 5s"

            # Probe center point of editor for overlays
            box = page.locator("#editor").bounding_box()
            if box:
                cx, cy = box["x"] + box["width"] / 2, box["y"] + 10
                top_id = page.evaluate("([x,y]) => { const el = document.elementFromPoint(x,y); return el && (el.id || el.className || el.tagName); }", [cx, cy])
                assert not (isinstance(top_id, str) and "examplesDrawer" in top_id), f"Examples drawer overlays editor: {top_id}"

            # No console or network errors that would break UI (ignore benign CSP-meta warning)
            filtered_errors = [e for e in errors if "frame-ancestors" not in (e[1] or "")]
            assert not filtered_errors, f"Console errors: {filtered_errors}"
            assert not fails, f"Failed requests: {fails}"
        finally:
            browser.close()

def test_live_translator_assist_toggles():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(1000)
        # Open settings
        page.click("#openAdvanced")
        # Enable symbol palette and voice
        if page.is_visible("#assistSymbols"):
            page.check("#assistSymbols")
        if page.is_visible("#assistVoice"):
            page.check("#assistVoice")
        # Open Assist and verify visible (right==0)
        page.click("#toggleChat")
        page.wait_for_selector("#chatDrawer", timeout=3000)
        right = page.eval_on_selector("#chatDrawer", "el => getComputedStyle(el).right")
        assert right and right.strip().startswith("0"), f"Chat drawer not visible, right={right}"
        # Palette visible only when enabled
        if page.is_checked("#assistSymbols"):
            assert page.is_visible("#chatSymbolPalette")
        # Mic and STT visible only when enabled
        if page.is_checked("#assistVoice"):
            assert page.is_visible("#chatMic")
        browser.close()


def test_live_examples_load_and_translate_triggers_request():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(800)
        # Open examples
        page.click("#openExamples")
        page.wait_for_selector("#examplesList")
        with page.expect_request(lambda r: "/llm/prompt-to-spec" in r.url):
            # Try the specific example; fallback to first available
            if page.is_visible('[data-ex-run-id="p2s_basic_1"]'):
                page.click('[data-ex-run-id="p2s_basic_1"]')
            else:
                btn = page.query_selector('[data-ex-run-id]')
                if btn:
                    btn.click()
        browser.close()


def test_live_output_tab_switch_sets_view():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(700)
        # Wait for tab controls to exist
        page.wait_for_selector("#outTabExpl")
        # Click and retry-read window.__outView
        page.click("#outTabExpl")
        def read_view():
            try:
                return page.evaluate("() => window.__outView || null")
            except Exception:
                return None
        deadline = time.time() + 2.0
        ok = False
        while time.time() < deadline:
            if read_view() == "expl":
                ok = True
                break
            page.wait_for_timeout(100)
        assert ok, "Output view did not switch to expl"
        page.click("#outTabTau")
        deadline2 = time.time() + 2.0
        ok2 = False
        while time.time() < deadline2:
            if read_view() == "tau":
                ok2 = True
                break
            page.wait_for_timeout(100)
        assert ok2, "Output view did not switch to tau"
        browser.close()


def test_live_privacy_mode_persists():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(500)
        page.click("#openAdvanced")
        # Toggle checkbox
        if page.is_visible("#privacyMode"):
            checked = page.is_checked("#privacyMode")
            if checked:
                page.uncheck("#privacyMode")
            else:
                page.check("#privacyMode")
            # Assert localStorage persisted
            val = page.evaluate("() => localStorage.getItem('tau_privacy_mode')")
            assert val in ("0", "1") and ((val == "1") != checked)
            # Reload and verify persistence
            page.reload()
            page.click("#openAdvanced")
            checked_after = page.is_checked("#privacyMode")
            assert checked_after != checked
        browser.close()


def test_live_examples_deep_link_runs():
    url = "https://www.tautranslator.ai/translator.html?example=p2s_basic_1&run=1"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        with page.expect_request(lambda r: "/llm/prompt-to-spec" in r.url):
            # nothing to click; deep link autoloads
            page.wait_for_timeout(100)
        browser.close()


def test_live_copy_out_toast():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(800)
        # Ensure Monaco output is initialized
        page.evaluate("() => { document.getElementById('outTau').value = 'always (p -> q)'; window.__outView='tau'; if(window.updateEditorOut){ window.updateEditorOut(); } }")
        page.wait_for_timeout(200)
        # Require that Monaco output exists; if not, skip
        has_editor_out = page.query_selector("#editorOut .monaco-editor") is not None
        if not has_editor_out:
            pytest.skip("Output Monaco not initialized on this run")
        page.click("#copyOut")
        # Wait for toast
        def toast_visible():
            try:
                return page.eval_on_selector('#toast', "el => getComputedStyle(el).opacity") == '1'
            except Exception:
                return False
        deadline = time.time() + 2.0
        ok = False
        while time.time() < deadline:
            if toast_visible():
                ok = True
                break
            page.wait_for_timeout(100)
        assert ok, "Copy toast did not appear"
        browser.close()

