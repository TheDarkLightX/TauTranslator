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


def test_live_translator_assist_toggles():
    url = "https://www.tautranslator.ai/translator.html"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
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
            # Open Assist
            page.click("#toggleChat")
            page.wait_for_selector("#chatDrawer", timeout=3000)
            # Palette visible only when enabled
            if page.is_checked("#assistSymbols"):
                assert page.is_visible("#chatSymbolPalette")
            # Mic and STT visible only when enabled
            if page.is_checked("#assistVoice"):
                assert page.is_visible("#chatMic")
        finally:
            browser.close()
        finally:
            browser.close()


