from __future__ import annotations

import re
import time
from typing import Tuple, List


# Heuristic email matcher (broad) to ensure redaction coverage
_EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CC_RE = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
_OPENROUTER_KEY_RE = re.compile(r"sk-or-[A-Za-z0-9]+")


def redact_pii(text: str) -> str:
    """Redact common PII/secrets from a string deterministically.

    This function is designed for logging and audit trails. It does not mutate
    user content for model inputs; call sites decide where to apply it.
    """
    if not text:
        return text
    redacted = text
    redacted = _EMAIL_RE.sub("[REDACTED:email]", redacted)
    redacted = _PHONE_RE.sub("[REDACTED:phone]", redacted)
    redacted = _SSN_RE.sub("[REDACTED:ssn]", redacted)
    # Replace likely credit-card-ish digit runs while avoiding timestamps by length heuristic
    redacted = _CC_RE.sub("[REDACTED:digits]", redacted)
    redacted = _OPENROUTER_KEY_RE.sub("[REDACTED:openrouter]", redacted)
    return redacted


_DISALLOWED_SNIPPETS = (
    # Obvious dangerous command markers
    "rm -rf /", "DROP TABLE", "; --", "--force", "curl|sh", "wget ",
    # Exec/shell
    "subprocess.", "os.system(", "exec(", "eval(",
    # Secrets hints
    "api key", "password=", "Authorization: Bearer ",
)


def moderate_text(text: str) -> Tuple[bool, List[str]]:
    """Lightweight rule-based moderation gate.

    Returns (ok, reasons). ok=False means the text should be rejected or escalated.
    """
    if not text:
        return True, []
    lower = text.lower()
    reasons: List[str] = []
    for snip in _DISALLOWED_SNIPPETS:
        if snip.lower() in lower:
            reasons.append(f"contains disallowed snippet: {snip}")
    # Excessive URL count heuristic
    url_count = len(re.findall(r"https?://", text))
    if url_count > 5:
        reasons.append("excessive external URLs")
    # Excessive length heuristic to avoid prompt stuffing
    if len(text) > 10000:
        reasons.append("input too long")
    return (len(reasons) == 0), reasons


class TokenBucket:
    """Simple in-memory token bucket for per-key rate limiting."""

    def __init__(self, capacity: int, refill_rate_per_sec: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate_per_sec
        self.tokens = capacity
        self.last = time.monotonic()

    def allow(self, cost: float = 1.0) -> bool:
        now = time.monotonic()
        elapsed = now - self.last
        self.last = now
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


def validate_chat_body(messages: List[dict]) -> Tuple[bool, List[str]]:
    """Validate chat messages for role, order, and size constraints.

    Rules:
    - roles limited to system|user|assistant
    - last message must be user
    - max messages per request: 30
    - max content length per message: 4000 chars
    """
    reasons: List[str] = []
    if not isinstance(messages, list) or not messages:
        return False, ["messages must be a non-empty list"]
    if len(messages) > 30:
        reasons.append("too many messages (max 30)")
    allowed_roles = {"system", "user", "assistant"}
    for idx, m in enumerate(messages):
        role = (m.get("role") or "").strip().lower() if isinstance(m, dict) else ""
        content = (m.get("content") or "") if isinstance(m, dict) else ""
        if role not in allowed_roles:
            reasons.append(f"invalid role at index {idx}")
        if not isinstance(content, str) or not content:
            reasons.append(f"empty content at index {idx}")
        if isinstance(content, str) and len(content) > 4000:
            reasons.append(f"content too long at index {idx}")
    last_role = (messages[-1].get("role") or "").strip().lower()
    if last_role != "user":
        reasons.append("last message must be from user")
    return (len(reasons) == 0), reasons


