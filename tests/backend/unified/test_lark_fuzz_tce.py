import os
import pytest

from backend.unified.domain.normalization import gate_tokens


def _allowed_chars(s: str) -> bool:
    import re
    return re.fullmatch(r"[A-Za-z0-9_,\s\(\)\-\>\|\&'\[\]<!=>]+", s) is not None


@pytest.mark.skipif(
    not os.path.exists(
        "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
    ),
    reason="TCE grammar file not present",
)
def test_lark_fuzzer_generates_gateable_tce():
    from lark import Lark
    from lark.tools import fuzzer

    grammar_path = (
        "src/tau_translator_omega/core_engine/cnl_parser/grammars/tce_fixed.lark"
    )
    with open(grammar_path, "r") as fh:
        g = fh.read()
    parser = Lark(g, start="start", parser="lalr", propagate_positions=False)
    # Generate a handful of random valid strings
    samples = [fuzzer.create_random_sentence(parser, start_symbol=parser.options.start)
               for _ in range(5)]
    for s in samples:
        # Wrap and gate
        out, _ = gate_tokens(f"always ({s})")
        assert out.lower().startswith("always ("), out
        assert out.endswith(")"), out
        assert _allowed_chars(out), out


