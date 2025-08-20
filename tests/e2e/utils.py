import time
from contextlib import contextmanager
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout


DEFAULT_URL = "https://www.tautranslator.ai/translator.html"
DEFAULT_API = "https://tau-translator-api.fly.dev"


def build_url(base: str = DEFAULT_URL, api: str = DEFAULT_API) -> str:
    params = {
        "api": api,
        "cb": str(int(time.time())),
    }
    sep = "&" if ("?" in base) else "?"
    return f"{base}{sep}{urlencode(params)}"


@contextmanager
def launch_page(url: str | None = None):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        # Inject a fetch spy before any page scripts run
        context.add_init_script(
            """
            (()=>{
              const origFetch = window.fetch;
              window.__e2e_requests = [];
              window.fetch = async (input, init={})=>{
                let path = '';
                try{
                  const u = (typeof input === 'string') ? new URL(input) : new URL(String(input));
                  path = u.pathname || '';
                }catch{}
                let bodyObj = null;
                try{ if(init && init.body){ bodyObj = JSON.parse(init.body); } }catch{}
                const headers = (init && init.headers) || {};
                try{ window.__e2e_requests.push({ path, headers, body: bodyObj, ts: Date.now() }); }catch{}
                const res = await origFetch(input, init);
                return res;
              };
            })();
            """
        )
        page = context.new_page()
        if url:
            page.goto(url, wait_until="load")
        try:
            yield page
        finally:
            browser.close()


def ensure_api_base(page, api: str = DEFAULT_API) -> None:
    try:
        page.fill("#apiBase", api)
        page.click("#saveApi")
    except Exception:
        pass


def toggle_settings(page, ensure_visible: bool = True) -> None:
    try:
        page.click("#openAdvanced")
        if ensure_visible:
            page.wait_for_selector("#controlsAdv", state="visible", timeout=2000)
    except Exception:
        pass


def set_privacy_mode(page, enabled: bool) -> None:
    try:
        # Ensure Settings visible and expand the Privacy details if collapsed
        try:
            # Click the summary labeled 'Privacy' to expand
            page.click("details >> text=Privacy")
        except Exception:
            pass
        if page.is_visible("#privacyMode"):
            if enabled:
                page.check("#privacyMode")
            else:
                page.uncheck("#privacyMode")
        elif page.is_visible("#localOnly"):
            # Backward-compatible toggle for older builds
            if enabled:
                page.check("#localOnly")
            else:
                page.uncheck("#localOnly")
    except Exception:
        pass


def set_input_text(page, text: str) -> None:
    try:
        page.wait_for_function("()=> window.editor !== undefined", timeout=4000)
        page.evaluate("(t)=>{ try{ editor.setValue(t); }catch(e){} }", text)
    except PwTimeout:
        page.fill("#input", text)


def click_translate(page) -> None:
    try:
        page.locator("#runMid").scroll_into_view_if_needed()
        page.click("#runMid", timeout=3000)
    except Exception:
        # Fallback: force click or dispatch event
        try:
            page.click("#runMid", force=True, timeout=1000)
        except Exception:
            try:
                page.evaluate("()=>{ const b=document.getElementById('runMid'); if(b) b.click(); }")
            except Exception:
                page.click("#run", force=True)


def wait_for_reasons(page, timeout_ms: int = 25000) -> str:
    # Prefer visible but fall back to attached or last-call heuristic
    deadline = page.evaluate("()=> Date.now()") + timeout_ms
    while True:
        try:
            # Visible
            el = page.query_selector("#outReasons")
            if el:
                # Return text regardless of visibility to avoid false negatives
                txt = el.inner_text()
                if txt.strip():
                    return txt
        except Exception:
            pass
        # Heuristic: if we made a request, allow a small settle delay then read text even if empty
        try:
            last = get_last_call(page)
            if last:
                page.wait_for_timeout(300)
                el = page.query_selector("#outReasons")
                if el:
                    return el.inner_text()
        except Exception:
            pass
        if page.evaluate("()=> Date.now()") > deadline:
            # Best effort return current text if present
            try:
                el = page.query_selector("#outReasons")
                if el:
                    return el.inner_text()
            except Exception:
                pass
            raise TimeoutError("Timed out waiting for reasons")


def get_last_call(page) -> dict:
    return page.evaluate("()=> window.__tau_last_call || null")


def select_output_tab(page, tab: str) -> None:
    ids = {
        "tau": "#outTabTau",
        "tce": "#outTabTce",
        "expl": "#outTabExpl",
        "module": "#outTabModule",
    }
    sel = ids.get(tab)
    if sel:
        page.click(sel)
        page.wait_for_timeout(200)


def clear_last_call(page) -> None:
    try:
        page.evaluate("()=>{ window.__tau_last_call = null; return true; }")
    except Exception:
        pass


def wait_for_last_call_path(page, expected_prefix: str, timeout_ms: int = 15000) -> dict:
    deadline = page.evaluate("()=> Date.now()") + timeout_ms
    while True:
        last = get_last_call(page) or {}
        if last and str(last.get("path", "")).startswith(expected_prefix):
            return last
        if page.evaluate("()=> Date.now()") > deadline:
            raise TimeoutError(f"Timed out waiting for last call path starting with {expected_prefix}")
        page.wait_for_timeout(200)


def select_editor_all(page) -> None:
    try:
        page.wait_for_function("()=> window.editor !== undefined", timeout=3000)
        page.evaluate(
            "()=>{ try{ const m=editor.getModel(); const end=m.getLineMaxColumn(1); editor.setSelection({startLineNumber:1,startColumn:1,endLineNumber:1,endColumn:end}); }catch(e){} }"
        )
    except Exception:
        pass


def get_last_request_with_prefix(page, prefix: str) -> dict:
    try:
        return page.evaluate(
            "(p)=>{ const arr=(window.__e2e_requests||[]).filter(x=>String(x.path||'').startsWith(p)); return arr.length? arr[arr.length-1] : null; }",
            prefix,
        ) or {}
    except Exception:
        return {}


def get_last_request_headers(page, prefix: str) -> dict:
    req = get_last_request_with_prefix(page, prefix)
    return (req.get("headers") if req else {}) or {}


def get_last_request_body(page, prefix: str) -> dict:
    req = get_last_request_with_prefix(page, prefix)
    return (req.get("body") if req else {}) or {}


def wait_for_request_path(page, prefix: str, timeout_ms: int = 15000) -> dict:
    deadline = page.evaluate("()=> Date.now()") + timeout_ms
    while True:
        req = get_last_request_with_prefix(page, prefix)
        if req:
            return req
        if page.evaluate("()=> Date.now()") > deadline:
            raise TimeoutError(f"Timed out waiting for request path starting with {prefix}")
        page.wait_for_timeout(200)


def set_checkbox(page, selector: str, checked: bool) -> None:
    try:
        if checked:
            page.check(selector)
        else:
            page.uncheck(selector)
    except Exception:
        pass


def choose_grammar_mode(page, mode: str) -> None:
    page.select_option("#grammarMode", mode)
    page.wait_for_timeout(100)
    # Ensure the correct row is visible
    if mode == "upload":
        page.wait_for_selector("#uploadRow", state="visible", timeout=2000)
    elif mode == "hosted":
        page.wait_for_selector("#hostedRow", state="visible", timeout=2000)


def attach_fixture_file(page, rel_path: str) -> None:
    # Requires grammar mode 'upload'
    page.set_input_files("#grammarFile", rel_path)
    # Wait for upload status to reflect loaded file
    page.wait_for_selector("#uploadStatus", timeout=3000)
    page.wait_for_timeout(150)


def set_hosted_grammar(page, value: str) -> None:
    # Requires grammar mode 'hosted'
    page.select_option("#hostedSelect", value)
    page.wait_for_timeout(100)


def get_out_view(page) -> str:
    try:
        return page.evaluate("()=> window.__outView || ''") or ""
    except Exception:
        return ""


def build_curl(page) -> str:
    try:
        return page.evaluate("()=> (typeof buildCurl==='function' ? buildCurl() : '')") or ""
    except Exception:
        return ""


