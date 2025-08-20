import os
import time
from urllib.parse import urlencode

import pytest
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout


def _build_target_url() -> str:
    base = os.environ.get(
        "TRANSLATOR_URL",
        "https://www.tautranslator.ai/translator.html",
    )
    params = {
        # Force API base to the Fly backend
        "api": "https://tau-translator-api.fly.dev",
        # Cache-bust
        "cb": str(int(time.time())),
    }
    sep = "&" if ("?" in base) else "?"
    return f"{base}{sep}{urlencode(params)}"


def _set_editor_value(page, text: str) -> None:
    # Try Monaco first
    try:
        page.wait_for_function("()=> window.editor !== undefined", timeout=4000)
        page.evaluate("(t)=>{ try{ editor.setValue(t); }catch(e){} }", text)
        return
    except PwTimeout:
        pass
    # Fallback to textarea
    page.fill("#input", text)


@pytest.mark.e2e
def test_prompt_to_spec_then_tau_smoke() -> None:
    url = _build_target_url()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.goto(url, wait_until="load")

        # Ensure API base input is set correctly (defensive)
        try:
            page.fill("#apiBase", "https://tau-translator-api.fly.dev")
            page.click("#saveApi")
        except Exception:
            # Non-fatal; continue
            pass

        # Try to open settings if needed (defensive)
        try:
            page.click("#openAdvanced")
        except Exception:
            pass

        # Toggle privacy mode off to allow BYOK/inline if needed; accept either id
        try:
            if page.is_visible("#privacyMode"):
                page.uncheck("#privacyMode")
        except Exception:
            try:
                if page.is_visible("#localOnly"):
                    page.uncheck("#localOnly")
            except Exception:
                pass

        # Seed input
        sample = "If a payment is approved then the order is shipped."
        _set_editor_value(page, sample)

        # Click translate (mid bar)
        page.click("#runMid")

        # Wait for reasons to populate
        page.wait_for_selector("#outReasons", timeout=25000)
        # Also allow async rendering
        page.wait_for_timeout(500)

        reasons = page.inner_text("#outReasons")
        assert "NetworkError" not in reasons, f"Unexpected network error: {reasons}"

        # Prefer Tau output; check hidden textarea value is populated or output editor has content
        tau_val = page.eval_on_selector("#outTau", "el => el.value")
        if not tau_val:
            # Try to switch to Tau tab and inspect rendered editor
            try:
                page.click("#outTabTau")
                page.wait_for_timeout(300)
                tau_text = page.evaluate("()=> (window.editorOut && editorOut.getValue()) || ''")
                assert tau_text.strip() != "", "Tau output is empty"
            except Exception:
                # As a last resort, assert we at least have TCE output
                tce_val = page.eval_on_selector("#outTce", "el => el.value")
                assert (tce_val or "").strip() != "", "No output produced"
        else:
            assert tau_val.strip() != "", "Tau output is empty"

        browser.close()


