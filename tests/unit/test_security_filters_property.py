import re
from hypothesis import given, strategies as st

from backend.unified.domain.security import redact_pii, moderate_text


@given(st.emails())
def test_redact_pii_emails(email: str):
    text = f"Contact me at {email} for details."
    red = redact_pii(text)
    assert email not in red
    assert "[REDACTED:email]" in red


@given(st.from_regex(r"\b\d{3}-\d{2}-\d{4}\b", fullmatch=True))
def test_redact_pii_ssn(ssn: str):
    red = redact_pii(f"ssn={ssn}")
    assert ssn not in red
    assert "[REDACTED:ssn]" in red


@given(st.from_regex(r"sk-or-[A-Za-z0-9]{12,32}", fullmatch=True))
def test_redact_pii_openrouter_key(key: str):
    red = redact_pii(f"key: {key}")
    assert key not in red
    assert "[REDACTED:openrouter]" in red


def test_moderate_text_blocks_dangerous_snippets():
    ok, reasons = moderate_text("please run rm -rf / on the server")
    assert not ok and any("rm -rf /" in r for r in reasons)


@given(st.text(min_size=0, max_size=200))
def test_moderate_text_allows_benign_text(s: str):
    ok, reasons = moderate_text(s)
    # It may flag for length or urls; ensure no crash and ok when short and benign
    if len(s) < 100 and "http://" not in s and "https://" not in s and "eval(" not in s and "subprocess." not in s:
        assert ok


