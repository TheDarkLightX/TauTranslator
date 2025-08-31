from __future__ import annotations

from typing import Protocol

from .normalization import normalize_inner_from_prompt


class SpecStrategy(Protocol):
    def normalize(self, orig_prompt_low: str, inner_text: str) -> str: ...


class WffStrategy:
    def normalize(self, orig_prompt_low: str, inner_text: str) -> str:
        return normalize_inner_from_prompt(orig_prompt_low, inner_text)


class RrStrategy:
    """Recurrence/relations leaning: prefer time-index forms when cues are present."""

    def normalize(self, orig_prompt_low: str, inner_text: str) -> str:
        # Stream equality patterns
        if (
            ("output" in orig_prompt_low and "input" in orig_prompt_low)
            and (
                "each time step" in orig_prompt_low
                or "time t" in orig_prompt_low
                or ("equals" in orig_prompt_low and "always" in orig_prompt_low)
            )
        ):
            return "(o1[t] = i1[t])"
        if ("output" in orig_prompt_low) and (
            "previous" in orig_prompt_low or "t-1" in orig_prompt_low
        ):
            return "(o1[t] = i1[t-1])"
        # Fall back to WFF normalization
        return normalize_inner_from_prompt(orig_prompt_low, inner_text)


def get_spec_strategy(spec_mode: str | None) -> SpecStrategy:
    if (spec_mode or "").lower() == "rr":
        return RrStrategy()
    return WffStrategy()


