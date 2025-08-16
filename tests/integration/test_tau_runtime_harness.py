import os
import pytest

from tools.tau_runtime_harness import evaluate_with_tau, is_configured, TauEvalResult


@pytest.mark.skipif(not is_configured(), reason="TAU_EVAL_CMD not configured")
def test_tau_accepts_simple_negation():
    text = "always (all x (!send_over_network(x)))\n"
    res = evaluate_with_tau(text)
    assert isinstance(res, TauEvalResult)
    assert res.ok, f"Tau rejected formula: rc={res.returncode}, stderr={res.stderr}"


@pytest.mark.skipif(not is_configured(), reason="TAU_EVAL_CMD not configured")
def test_tau_accepts_causal_and_guard():
    text = "always ((payment_approved and !maintenance) -> order_shipped)\n"
    res = evaluate_with_tau(text)
    assert res.ok, f"Tau rejected causal/guard: {res.stderr}"


@pytest.mark.skipif(not is_configured(), reason="TAU_EVAL_CMD not configured")
def test_tau_nested_quantifiers():
    text = "always (all x (login_success(x) -> ex y (active_for(x,y))))\n"
    res = evaluate_with_tau(text)
    assert res.ok, f"Tau rejected nested quantifiers: {res.stderr}"


@pytest.mark.skipif(not is_configured(), reason="TAU_EVAL_CMD not configured")
def test_tau_boolean_composition():
    text = "always ((sensor_high or manual_override) -> alarm_on)\n"
    res = evaluate_with_tau(text)
    assert res.ok, f"Tau rejected boolean combo: {res.stderr}"


