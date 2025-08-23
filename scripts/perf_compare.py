import json
import time
import socket
from contextlib import closing

from playwright.sync_api import sync_playwright
import subprocess, sys, os


def _ensure_docs_server(host: str = "127.0.0.1", port: int = 8777) -> str:
    def _is_open(h, p):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.2)
            return s.connect_ex((h, p)) == 0

    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _ensure_svelte_preview(host: str = "127.0.0.1", port: int = 5199) -> str:
    def _is_open(h, p):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(0.2)
            return s.connect_ex((h, p)) == 0
    if not _is_open(host, port):
        env = os.environ.copy()
        subprocess.Popen(["npm", "run", "preview"], cwd=os.path.join(os.getcwd(), "apps/sveltekit"), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(1.0)
    return f"http://{host}:{port}"


def _nav_metrics(page):
    nav = page.evaluate("() => { const n = performance.getEntriesByType('navigation')[0]; return n ? ({ startTime:n.startTime, responseEnd:n.responseEnd, domContentLoadedEventEnd:n.domContentLoadedEventEnd, loadEventEnd:n.loadEventEnd, type:n.type }) : null }")
    return nav or {}


def _now(page):
    return float(page.evaluate("() => performance.now()"))


def measure_translator(url: str, path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        t0 = _now(page)
        page.goto(url + path, wait_until="domcontentloaded")
        dcl_now = _now(page)
        # Wait briefly for UI ready flag or editor visibility
        ui_ready_ms = None
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline:
                ready = page.evaluate("() => !!window.TAU_UI_READY");
                if ready:
                    ui_ready_ms = _now(page)
                    break
                time.sleep(0.05)
        except Exception:
            pass
        # Input editor readiness (Monaco or fallback)
        in_ready = None
        try:
            if page.query_selector("#editor .monaco-editor"):
                in_ready = _now(page)
            else:
                # Fallback textarea visible counts as ready
                page.wait_for_selector("#input", timeout=1500)
                in_ready = _now(page)
        except Exception:
            in_ready = None
        nav = _nav_metrics(page)
        browser.close()
        return {
            "domcontentloaded_ms": dcl_now - t0,
            "ui_ready_ms": (ui_ready_ms - t0) if ui_ready_ms else None,
            "input_ready_ms": (in_ready - t0) if in_ready else None,
            "navigation": nav,
        }


def measure_translator_cm(url: str, path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        t0 = _now(page)
        page.goto(url + path, wait_until="domcontentloaded")
        dcl_now = _now(page)
        # Wait for CodeMirror content or fallback
        cm_in_ready = None
        try:
            page.wait_for_selector("#cmIn .cm-content, #inFallback", timeout=2000)
            cm_in_ready = _now(page)
        except Exception:
            pass
        # UI ready flag if present
        ui_ready_ms = None
        try:
            deadline = time.time() + 3.0
            while time.time() < deadline:
                ready = page.evaluate("() => !!window.TAU_UI_READY")
                if ready:
                    ui_ready_ms = _now(page)
                    break
                time.sleep(0.05)
        except Exception:
            pass
        nav = _nav_metrics(page)
        browser.close()
        return {
            "domcontentloaded_ms": dcl_now - t0,
            "ui_ready_ms": (ui_ready_ms - t0) if ui_ready_ms else None,
            "input_ready_ms": (cm_in_ready - t0) if cm_in_ready else None,
            "navigation": nav,
        }


def main():
    base = _ensure_docs_server()
    monaco = measure_translator(base, "/translator.html")
    cm6 = measure_translator_cm(base, "/translator_cm.html")
    sbase = _ensure_svelte_preview()
    svelte = measure_translator_cm(sbase, "/")
    out = {
        "links": {
            "monaco": base + "/translator.html",
            "codemirror": base + "/translator_cm.html",
            "sveltekit": sbase + "/"
        },
        "monaco": monaco,
        "cm6": cm6,
        "sveltekit": svelte,
        "delta_ms": {
            "domcontentloaded": (cm6.get("domcontentloaded_ms") or 0) - (monaco.get("domcontentloaded_ms") or 0),
            "ui_ready": (cm6.get("ui_ready_ms") or 0) - (monaco.get("ui_ready_ms") or 0),
            "input_ready": (cm6.get("input_ready_ms") or 0) - (monaco.get("input_ready_ms") or 0),
        }
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()


