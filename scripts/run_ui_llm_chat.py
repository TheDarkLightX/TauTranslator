#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def _read_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_KEY", "").strip()
    if key:
        return key
    p = Path.home() / ".secrets" / "openrouter_key"
    if p.exists():
        try:
            return p.read_text(encoding="utf-8").strip()
        except Exception:
            return ""
    return ""


def main() -> int:
    url = os.environ.get(
        "TAU_UI_URL",
        "http://127.0.0.1:8777/translator_cm.html?api=https://tau-translator-api.fly.dev",
    )
    question = (
        os.environ.get("TAU_CHAT_QUESTION")
        or "How do I explain the speed of light as a logical invariant?"
    )
    byok = _read_openrouter_key()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")

        # Ensure Privacy OFF (so BYOK header is sent)
        try:
            page.evaluate("() => { localStorage.setItem('tau_privacy_mode','0'); }")
        except Exception:
            pass

        # Set BYOK via input + Save for clarity
        if byok:
            try:
                page.fill("#byok", byok)
                page.click("#saveByok")
            except Exception:
                # fallback: persist directly
                try:
                    page.evaluate("(k) => localStorage.setItem('tau_byok_openrouter', k)", byok)
                except Exception:
                    pass

        # Try built-in Test LLM first (pings /llm/chat and opens chat)
        try:
            page.click("#testLlm")
        except Exception:
            pass

        # Open chat and send question
        try:
            page.click("#toggleChat")
        except Exception:
            pass
        try:
            page.fill("#chatInput", question)
            page.click("#chatSend")
        except Exception:
            pass

        # Wait up to 30s for assistant reply or provider line
        for _ in range(60):
            nodes = page.query_selector_all("#chatMessages > div")
            if len(nodes) >= 2:
                break
            page.wait_for_timeout(500)

        messages = page.eval_on_selector_all(
            "#chatMessages > div", "els => els.map(el => el.textContent)"
        )
        reasons = ""
        try:
            reasons = page.inner_text("#reasons")
        except Exception:
            pass

        print("---- CHAT MESSAGES ----")
        for line in messages[-6:]:
            print(line)
        if reasons and reasons.strip():
            print("---- REASONS ----")
            print(reasons)

        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


