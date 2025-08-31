"""Tau Controlled English (TCE) ↔ Tau Language Translator
=======================================================
Minimal functional implementation that relies on simple regular
expression rules.  It acts as a placeholder until the full Lark-
based parser is integrated.  The goal is to unblock tests and
allow end-to-end flows via the TranslatorRegistry.

The module adheres to railway-oriented programming by returning
`Result` objects (`Success` or `Failure`) rather than raising
exceptions.

Keeping file ≤ 300 lines for maintainability.
"""

from __future__ import annotations

import re
from typing import Pattern, Tuple, Callable

from backend.unified.core.result_enhanced import Result, Success, Failure

__all__ = ["TceLarkTranslator"]


class _Rule:
    """A bidirectional mapping rule between Controlled English and Tau."""

    def __init__(
        self,
        ce_pattern: str,
        tau_pattern: str,
        ce_to_tau: Callable[[re.Match[str]], str],
        tau_to_ce: Callable[[re.Match[str]], str],
    ) -> None:
        self.ce_regex: Pattern[str] = re.compile(ce_pattern, flags=re.IGNORECASE)
        self.tau_regex: Pattern[str] = re.compile(tau_pattern, flags=re.IGNORECASE)
        self.ce_to_tau = ce_to_tau
        self.tau_to_ce = tau_to_ce

    # ------------------------------------------------------------------
    # Conversion helpers
    # ------------------------------------------------------------------
    def try_ce_to_tau(self, text: str) -> Tuple[bool, str]:
        m = self.ce_regex.fullmatch(text.strip())
        if not m:
            return False, text
        return True, self.ce_to_tau(m)

    def try_tau_to_ce(self, text: str) -> Tuple[bool, str]:
        m = self.tau_regex.fullmatch(text.strip())
        if not m:
            return False, text
        return True, self.tau_to_ce(m)


class TceLarkTranslator:  # pylint: disable=too-few-public-methods
    """Placeholder translator using regex heuristics.

    Parameters
    ----------
    max_chars : int, optional
        Safety valve to avoid runaway output.  Translation fails if
        generated text exceeds this length.
    """

    # ------------------------------------------------------------------
    # Init / rule setup
    # ------------------------------------------------------------------
    def __init__(self, max_chars: int = 10_000) -> None:
        self._max_chars = max_chars
        self._rules = self._build_rules()

    # ------------------------------------------------------------------
    # Public API (TranslatorProtocol compliance)
    # ------------------------------------------------------------------
    def translate(self, source: str, source_lang: str, target_lang: str) -> Result[str]:
        source_lang = source_lang.upper()
        target_lang = target_lang.upper()

        if source_lang == target_lang:
            return Success(source)  # No-op

        if source_lang == "CONTROLLED_ENGLISH" and target_lang == "TAU":
            return self._ce_to_tau(source)
        if source_lang == "TAU" and target_lang == "CONTROLLED_ENGLISH":
            return self._tau_to_ce(source)

        return Failure(
            "UNSUPPORTED_DIRECTION",
            f"TceLarkTranslator does not support {source_lang} → {target_lang}",
        )

    # ------------------------------------------------------------------
    # Internal conversion routines
    # ------------------------------------------------------------------
    def _ce_to_tau(self, text: str) -> Result[str]:
        for rule in self._rules:
            matched, out = rule.try_ce_to_tau(text)
            if matched:
                if len(out) > self._max_chars:
                    return Failure("OUTPUT_TOO_LARGE", "Translation exceeds max_chars limit")
                return Success(out)
        return Failure("CE_TO_TAU_NO_RULE", "No matching Controlled English rule found")

    def _tau_to_ce(self, text: str) -> Result[str]:
        for rule in self._rules:
            matched, out = rule.try_tau_to_ce(text)
            if matched:
                if len(out) > self._max_chars:
                    return Failure("OUTPUT_TOO_LARGE", "Translation exceeds max_chars limit")
                return Success(out)
        return Failure("TAU_TO_CE_NO_RULE", "No matching Tau rule found")

    # ------------------------------------------------------------------
    # Rule definitions (expand incrementally)
    # ------------------------------------------------------------------
    @staticmethod
    def _build_rules() -> list[_Rule]:
        # Rule 1 – always equality
        ce_pat = r"always\s+(?P<lhs>[a-zA-Z][\w]*)\s+equals\s+(?P<rhs>[a-zA-Z][\w]*)\."
        tau_pat = r"always\s*\(\s*(?P<lhs>[a-zA-Z][\w]*)\s*=\s*(?P<rhs>[a-zA-Z][\w]*)\s*\)"

        def ce_to_tau(m: re.Match[str]) -> str:  # noqa: D401
            return f"always ({m.group('lhs')} = {m.group('rhs')})"

        def tau_to_ce(m: re.Match[str]) -> str:
            return f"always {m.group('lhs')} equals {m.group('rhs')}."

        rules = [_Rule(ce_pat, tau_pat, ce_to_tau, tau_to_ce)]

        # Rule 2 – previous value equality (supports 0/1 literals)
        prev_ce = r"always\s+previous\s+(?P<var>[a-zA-Z][\w]*)\s+equals\s+(?P<val>[01])\."
        prev_tau = r"always\s*\(\s*(?P<var>[a-zA-Z][\w]*)\[t-1\]\s*=\s*(?P<val>[01])\s*\)"

        def prev_ce_to_tau(m: re.Match[str]) -> str:
            return f"always ({m.group('var')}[t-1] = {m.group('val')})"

        def prev_tau_to_ce(m: re.Match[str]) -> str:
            return f"always previous {m.group('var')} equals {m.group('val')}."

        # Rule 3 – simple if-then-else conditional
        ce_cond = (
            r"if\s+(?P<cond>.+?)\s+then\s+(?P<true>.+?)\s+else\s+(?P<false>.+?)\."
        )
        # Tau side needs no leading keyword
        tau_cond = (
            r"\(?(?P<cond>.+?)\)?\s*\?\s*(?P<true>.+?)\s*:\s*(?P<false>.+?)"
        )

        def cond_ce_to_tau(m: re.Match[str]) -> str:
            return f"({m.group('cond')} ? {m.group('true')} : {m.group('false')})"

        def cond_tau_to_ce(m: re.Match[str]) -> str:
            return f"if {m.group('cond')} then {m.group('true')} else {m.group('false')}."

        rules.append(_Rule(prev_ce, prev_tau, prev_ce_to_tau, prev_tau_to_ce))
        rules.append(_Rule(ce_cond, tau_cond, cond_ce_to_tau, cond_tau_to_ce))

        # Rule 4 – binary AND
        ce_and = r"(?P<left>[a-zA-Z][\w]*)\s+and\s+(?P<right>[a-zA-Z][\w]*)\."
        tau_and = r"\(?(?P<left>[a-zA-Z][\w]*)\s*&\s*(?P<right>[a-zA-Z][\w]*)\)?"

        def and_ce_to_tau(m: re.Match[str]) -> str:
            return f"({m.group('left')} & {m.group('right')})"

        def and_tau_to_ce(m: re.Match[str]) -> str:
            return f"{m.group('left')} and {m.group('right')}."

        # Rule 5 – binary OR
        ce_or = r"(?P<left>[a-zA-Z][\w]*)\s+or\s+(?P<right>[a-zA-Z][\w]*)\."
        tau_or = r"\(?(?P<left>[a-zA-Z][\w]*)\s*\|\s*(?P<right>[a-zA-Z][\w]*)\)?"

        def or_ce_to_tau(m: re.Match[str]) -> str:
            return f"({m.group('left')} | {m.group('right')})"

        def or_tau_to_ce(m: re.Match[str]) -> str:
            return f"{m.group('left')} or {m.group('right')}."

        rules.append(_Rule(ce_and, tau_and, and_ce_to_tau, and_tau_to_ce))
        rules.append(_Rule(ce_or, tau_or, or_ce_to_tau, or_tau_to_ce))

        return rules 