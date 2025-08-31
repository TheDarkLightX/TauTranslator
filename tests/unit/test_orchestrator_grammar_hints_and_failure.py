from backend.unified.domain.llm_orchestrator import ChatOrchestrator
from backend.unified.infrastructure.llm_providers import LLMProvider, LLMRequest
from backend.unified.core.result_enhanced import Success, Failure


class FailingProvider(LLMProvider):
    def generate(self, request: LLMRequest):
        return Failure("OPENROUTER_HTTP_500", "server error")


class HintedProvider(LLMProvider):
    def generate(self, request: LLMRequest):
        # include multiple lines to exercise sanitize and hint paths
        return Success(type("Resp", (), {"text": "Note: always (p -> q)\nExtra", "usage": {}})())


def _msg(txt: str):
    return [{"role": "system", "content": "rules"}, {"role": "user", "content": txt}]


def test_orchestrator_failure_path():
    orch = ChatOrchestrator(FailingProvider())
    reply, tce, tau, reasons, prov = orch.generate_tce(_msg("x"))
    assert reply == "" and tce == "" and tau is None and reasons and prov


def test_orchestrator_grammar_hint_path():
    orch = ChatOrchestrator(HintedProvider())
    reply, tce, tau, reasons, prov = orch.generate_tce(_msg("x"))
    assert tce.lower().startswith("always (")

