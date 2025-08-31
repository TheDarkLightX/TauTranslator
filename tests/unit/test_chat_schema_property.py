from hypothesis import given, strategies as st

from backend.unified.domain.security import validate_chat_body


def _role_strategy():
    return st.sampled_from(["system", "user", "assistant"])


def _message_strategy():
    return st.fixed_dictionaries({
        "role": _role_strategy(),
        "content": st.text(min_size=1, max_size=50),
    })


@given(st.lists(_message_strategy(), min_size=1, max_size=10).map(lambda msgs: msgs[:-1] + [{"role": "user", "content": "ok"}]))
def test_validate_chat_body_accepts_valid_roles_and_last_user(msgs):
    ok, reasons = validate_chat_body(msgs)
    assert ok, reasons


@given(st.lists(_message_strategy(), min_size=1, max_size=10))
def test_validate_chat_body_rejects_last_not_user(msgs):
    # Force last role not user
    msgs[-1]["role"] = "assistant"
    ok, reasons = validate_chat_body(msgs)
    assert not ok and any("last message must be from user" in r for r in reasons)


