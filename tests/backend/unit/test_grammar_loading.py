import pytest
from lark import Lark
from lark.exceptions import GrammarError


def test_load_controlled_grammar():
    """Tests that the Tau Controlled English grammar can be loaded by Lark without errors."""
    try:
        with open("src/tau_translator_omega/core_engine/parsers/grammars/tau_controlled.lark", "r", encoding="utf-8") as f:
            grammar = f.read()
        Lark(grammar, start='start', parser='lalr')
    except GrammarError as e:
        pytest.fail(f"Failed to load grammar. Lark Error: \n{e}")
