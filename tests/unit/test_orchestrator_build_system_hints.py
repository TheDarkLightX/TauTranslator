from backend.unified.domain.llm_orchestrator import ChatOrchestrator


def test_build_system_with_grammar_inline_and_ref():
    base = "rules"
    extra = "extra"
    grammar_inline = {"name": "tau", "content": "forall x exists y always -> && || T F"}
    grammar_ref = {"id": "tce", "version": "v1"}
    out = ChatOrchestrator._build_system(base, extra, grammar_inline, grammar_ref)
    assert "GrammarInline:" in out and "GrammarRef:" in out
    assert "Allowed tokens:" in out

