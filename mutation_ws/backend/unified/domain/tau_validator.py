"""
Tau syntax validator using the project's TGF grammar pipeline.

This module loads a Tau grammar from a user-provided path, then parses
provided Tau text using the generated Lark grammar. We do not bundle,
download, or autodetect IDNI Tau assets to respect license constraints.

Public API:
- validate_tau_syntax(tau_text: str) -> dict
  Returns {"valid": bool, "errors": list[str]} deterministically.

Notes:
- Grammar path resolution order:
  1) TAU_TGF_PATH environment variable, if present and exists
  2) grammars/tau.tgf, if present
  Otherwise, grammar-backed validation is disabled.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
import os


@dataclass(frozen=True)
class TauValidationResult:
    valid: bool
    errors: List[str]


def _resolve_grammar_path() -> Optional[Path]:
    """Resolve a local tau.tgf path.

    We intentionally avoid network download/autodetection of IDNI assets.
    """
    # 1) Explicit env
    env_path = os.getenv("TAU_TGF_PATH")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    # 2) Project-local grammars/tau.tgf
    local = Path("grammars/tau.tgf")
    if local.exists():
        return local
    return None


def validate_tau_syntax(tau_text: str) -> dict:
    """Validate Tau syntax using the TGF grammar if available.

    Returns a dictionary with keys:
    - valid: bool
    - errors: list[str]
    """
    tau = (tau_text or "").strip()
    if not tau:
        return {"valid": False, "errors": ["Empty Tau text"]}

    grammar_path = _resolve_grammar_path()
    if grammar_path is None or not grammar_path.exists():
        # Deterministic minimal structural check as a last resort
        # Accept both atemporal WFF and always-wrapped forms.
        errs: List[str] = []
        # Quick parentheses balance check
        bal = 0
        for ch in tau:
            if ch == "(":
                bal += 1
            elif ch == ")":
                bal -= 1
                if bal < 0:
                    errs.append("Unbalanced parentheses")
                    break
        if bal != 0:
            errs.append("Unbalanced parentheses")
        # Token whitelist (basic)
        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_ ()!->|&<>=:\n\t")
        if any((c not in allowed) for c in tau):
            errs.append("Contains unsupported characters")
        return {"valid": len(errs) == 0, "errors": errs}

    # Grammar-backed parse
    try:
        # Lazy imports to avoid hard dependency in environments without core engine
        from tau_translator_omega.infrastructure.grammar_io import GrammarRepository
        from tau_translator_omega.core_engine.grammar_processing import (
            TGFGrammarService,
            TGFGrammarParser,
            TGFGrammarConverter,
        )
        from tau_translator_omega.core_engine.parsers.grammar_driven_parser import (
            GrammarDrivenParser as EnhancedParser,
        )

        repo = GrammarRepository(grammar_dir=grammar_path.parent, config_file=grammar_path.parent / "grammar_config.json")
        # Load content
        content_result = repo.read_grammar_file(grammar_path.name)
        if not content_result.is_success():
            return {"valid": False, "errors": ["Failed to read grammar file"]}
        content = content_result.unwrap()

        rules, terminals, non_terminals, directives = TGFGrammarParser.parse_tgf_content(content)
        # Build loaded grammar structure expected by converter
        from tau_translator_omega.core_engine.grammar_processing import LoadedGrammar
        loaded = LoadedGrammar(
            filename=grammar_path.name,
            original_name=grammar_path.name,
            type=".tgf",
            content=content,
            is_active=True,
            rules=rules,
            terminals=terminals,
            non_terminals=non_terminals,
            directives=directives,
        )
        lark_grammar, _ = TGFGrammarConverter.to_lark_grammar(loaded)
        parser = EnhancedParser(lark_grammar)
        _ = parser.parse(tau)
        return {"valid": True, "errors": []}
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}


