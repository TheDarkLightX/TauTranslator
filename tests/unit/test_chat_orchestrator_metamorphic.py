from backend.unified.domain.llm_orchestrator import ChatOrchestrator
from backend.unified.infrastructure.llm_providers import LLMProvider, LLMRequest
from backend.unified.core.result_enhanced import Success


class DeterministicProvider(LLMProvider):
    def generate(self, request: LLMRequest):
        # Return a completion that requires sanitization to extract always(...)
        return Success(type("Resp", (), {"text": "Response: always (payment_approved -> order_shipped)", "usage": {}})())


def _messages_of(text: str):
    return [
        {"role": "user", "content": text},
    ]


def test_metamorphic_case_insensitivity():
    orch = ChatOrchestrator(DeterministicProvider())
    reply1, tce1, tau1, _, _ = orch.generate_tce(_messages_of("If a payment is approved then the order is shipped."))
    reply2, tce2, tau2, _, _ = orch.generate_tce(_messages_of("IF A PAYMENT IS APPROVED THEN THE ORDER IS SHIPPED."))
    assert tce1.strip().lower().startswith("always (") and tce2.strip().lower().startswith("always (")
    assert (tau1 is None) or isinstance(tau1, str)
    assert (tau2 is None) or isinstance(tau2, str)


def test_metamorphic_whitespace_variation():
    orch = ChatOrchestrator(DeterministicProvider())
    reply1, tce1, tau1, _, _ = orch.generate_tce(_messages_of("If a payment is approved then the order is shipped."))
    reply3, tce3, tau3, _, _ = orch.generate_tce(_messages_of("   If a payment is   approved then   the order is shipped.   "))
    assert tce1.strip().lower().startswith("always (") and tce3.strip().lower().startswith("always (")
    assert (tau1 is None) or isinstance(tau1, str)
    assert (tau3 is None) or isinstance(tau3, str)


