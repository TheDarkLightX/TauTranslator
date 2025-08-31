"""
Grammar Knowledge Pack builder: safe summaries/examples/lexicon from TCE/Tau grammars.
Does not embed raw grammar text; outputs are license-safe.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any
import json

from ..core.result_enhanced import Result, Success, Failure


@dataclass
class RuleSummary:
    name: str
    summary: str
    examples: List[str]


@dataclass
class KnowledgePack:
    grammar_id: str
    version: str
    lexicon: List[str]
    rules: List[RuleSummary]
    provenance: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2, ensure_ascii=False)


class GrammarKnowledgePackBuilder:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)

    def build_minimal(self, grammar_id: str, version: str) -> Result[KnowledgePack]:
        try:
            # Minimal lexicon and two rule stubs to bootstrap flows
            lexicon = ["always", "sometimes", "forall", "exists", "equals", "is greater than"]
            rules = [
                RuleSummary(
                    name="quantified_expr",
                    summary="Quantified property over variables using forall/exists.",
                    examples=["forall x : P(x)", "exists y : Q(y)"]
                ),
                RuleSummary(
                    name="comparison",
                    summary="Comparison between two terms using equals/relational operators.",
                    examples=["x equals 5", "x is greater than 5"]
                ),
            ]
            kp = KnowledgePack(
                grammar_id=grammar_id,
                version=version,
                lexicon=lexicon,
                rules=rules,
                provenance={"source": "derived", "safety": "no raw grammar embedded"}
            )

            out_dir = self.output_dir / grammar_id / version
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "pack.json").write_text(kp.to_json(), encoding="utf-8")
            return Success(kp)
        except Exception as e:
            return Failure("PACK_BUILD_ERROR", str(e))


