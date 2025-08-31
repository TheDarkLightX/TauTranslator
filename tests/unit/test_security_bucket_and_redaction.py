import time
from backend.unified.domain.security import TokenBucket, redact_pii


def test_token_bucket_allows_then_limits():
    b = TokenBucket(capacity=2, refill_rate_per_sec=0.0)
    assert b.allow()
    assert b.allow()
    assert not b.allow()


def test_token_bucket_refill():
    b = TokenBucket(capacity=1, refill_rate_per_sec=10.0)  # 10 tokens/sec
    assert b.allow()  # consume
    assert not b.allow()
    time.sleep(0.12)
    assert b.allow()  # refilled ~1.2 tokens


def test_redact_phone_and_cc():
    s = "call 555-123-4567; card 4111 1111 1111 1111"
    out = redact_pii(s)
    assert "555-123-4567" not in out
    import re
    # No long digit runs (13-19) remain
    assert not re.search(r"(?:\d[ -]?){13,19}", out)

