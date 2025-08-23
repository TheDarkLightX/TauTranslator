import json
import time
import socket
from contextlib import closing
import subprocess, sys, os
from playwright.sync_api import sync_playwright


def _is_open(host, port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


def ensure_docs():
    host, port = "127.0.0.1", 8777
    if not _is_open(host, port):
        subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--directory", "docs", "--bind", host])
        time.sleep(1.0)
    return f"http://{host}:{port}"


def ensure_svelte():
    host, port = "127.0.0.1", 5199
    if not _is_open(host, port):
        env = os.environ.copy()
        subprocess.Popen(["npm", "run", "preview"], cwd=os.path.join(os.getcwd(), "apps/sveltekit"), env=env, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        time.sleep(1.0)
    return f"http://{host}:{port}"


def check(page, name: str):
    info = {"name": name}
    # common flags
    info["ui_ready"] = bool(page.evaluate("() => !!window.TAU_UI_READY"))
    info["oracle_exists"] = bool(page.evaluate("() => typeof window.__tau_last_call !== 'undefined'"))
    # editors
    info["monaco_in"] = page.query_selector("#editor .monaco-editor") is not None
    info["monaco_out"] = page.query_selector("#editorOut .monaco-editor") is not None
    info["cm_in"] = page.query_selector("#cmIn .cm-content") is not None
    info["cm_out"] = page.query_selector("#cmOut .cm-content") is not None
    info["fallback_in"] = page.query_selector("#input, #inFallback") is not None
    info["fallback_out"] = page.query_selector("#outputFallback, #outFallback") is not None
    # buttons
    info["btn_translate"] = page.query_selector("#runMid, #run, #btnTranslate") is not None
    info["btn_examples"] = page.query_selector("#openExamples, #btnExamples") is not None
    info["btn_settings"] = page.query_selector("#openAdvanced, #btnSettings") is not None
    info["btn_assist"] = page.query_selector("#toggleChat, #btnAssist") is not None
    # assist palette
    info["assist_palette"] = page.query_selector("#chatSymbolPalette") is not None
    return info


def main():
    docs = ensure_docs()
    svelte = ensure_svelte()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        res = {}
        for name, url in [
            ("monaco", docs + "/translator.html"),
            ("cm6_docs", docs + "/translator_cm.html"),
            ("sveltekit", svelte + "/"),
        ]:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_timeout(250)
            res[name] = check(page, name)
            page.close()
        browser.close()
        print(json.dumps({"links": {"monaco": docs+"/translator.html", "cm6": docs+"/translator_cm.html", "sveltekit": svelte+"/"}, "ui": res}, indent=2))


if __name__ == "__main__":
    main()


