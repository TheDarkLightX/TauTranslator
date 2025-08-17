"""
Generate a corpus of Tau formulas (and optional predicate definitions) plus
natural-language prompts for end-to-end testing.

Outputs a list of entries in memory so tests can import and iterate without
materializing large JSON assets in the repo.

Each entry:
{
  "id": str,
  "category": str,
  "defs": list[str],         # REPL definition lines ending with '.'
  "tau": str,               # Tau formula (no trailing '.')
  "expected_sat": bool,     # True if we expect satisfiable
  "prompts": list[str],     # English prompts that should map to this
}

Notes:
- We keep constructs strictly within the grammar in parser/tau.tgf:
  logical: !, &&, ||, ->, <->, <- ; quantifiers: all, ex ; temporal: always/sometimes
- For predicate atoms P(x) we emit definitions like P[0](x) := T. to ensure sat.
- We avoid relying on shell parsing by letting tests feed REPL commands via stdin.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class CorpusEntry:
    id: str
    category: str
    defs: List[str]
    tau: str
    expected_sat: bool
    prompts: List[str]


def _p0(name: str) -> str:
    return f"{name}[0]()"


def _p1(name: str, var: str) -> str:
    return f"{name}[0]({var})"


def _defs_0(names: List[str], value: str) -> List[str]:
    return [f"{n}[0]() := {value}." for n in names]


def _defs_1(name: str, var: str, value: str) -> List[str]:
    return [f"{name}[0]({var}) := {value}."]


def _always(phi: str) -> str:
    return f"always {phi}"


def _sometimes(phi: str) -> str:
    return f"sometimes {phi}"


def _imp(a: str, b: str) -> str:
    return f"({a} -> {b})"


def _and(a: str, b: str) -> str:
    return f"({a} && {b})"


def _or(a: str, b: str) -> str:
    return f"({a} || {b})"


def _neg(a: str) -> str:
    return f"(!{a})"


def _all(var: str, phi: str) -> str:
    return f"all {var} {phi}"


def _ex(var: str, phi: str) -> str:
    return f"ex {var} {phi}"


def _stream_eq(lhs: str, rhs: str) -> str:
    return f"({lhs} = {rhs})"


def build_corpus(max_entries: int = 250) -> List[CorpusEntry]:
    entries: List[CorpusEntry] = []

    # 1) Base logical truths/falsities
    base: List[CorpusEntry] = [
        CorpusEntry("base_always_T", "base", [], _always("T"), True, ["Always true."]),
        CorpusEntry("base_not_F", "base", [], _neg("F"), True, ["Not false."]),
        CorpusEntry("base_T_and_T", "base", [], _and("T", "T"), True, ["True and true."]),
        CorpusEntry("base_T_or_F", "base", [], _or("T", "F"), True, ["True or false."]),
        CorpusEntry("base_T_implies_T", "base", [], _imp("T", "T"), True, ["If true then true."]),
        CorpusEntry("base_T_equiv_T", "base", [], "(T <-> T)", True, ["True is equivalent to true."]),
    ]
    entries.extend(base)

    # 2) Streams equality
    streams: List[CorpusEntry] = [
        CorpusEntry(
            "stream_o_eq_i",
            "streams",
            [],
            _always(_stream_eq("o1[t]", "i1[t]")),
            True,
            ["Output always equals input at each time step.", "o1 at time t equals i1 at time t always."],
        ),
        CorpusEntry(
            "stream_guard_implies",
            "streams",
            [],
            _always(_imp("(i1[t] != 1)", "(o1[t] != 0)")),
            True,
            ["If input is not 1 then output is not 0, at all times."],
        ),
        CorpusEntry(
            "stream_lookback",
            "streams",
            [],
            _always(_stream_eq("o1[t]", "i1[t-1]")),
            True,
            ["Output at time t equals input at previous step."],
        ),
    ]
    entries.extend(streams)

    # 3) Predicates 0-arity implication
    defs_imp = _defs_0(["payment_approved", "order_shipped"], "T")
    entries.append(
        CorpusEntry(
            "pred0_imp",
            "predicates0",
            defs_imp,
            _imp(_p0("payment_approved"), _p0("order_shipped")),
            True,
            ["If a payment is approved then the order is shipped."],
        )
    )

    # 4) Unary predicates with quantifiers
    entries.append(
        CorpusEntry(
            "pred1_all_not",
            "predicates1",
            _defs_1("send_over_network", "x", "F"),
            _always(_all("x", _neg(_p1("send_over_network", "x")))),
            True,
            ["Never send data over the network.", "For all x, not send_over_network(x), always."],
        )
    )
    entries.append(
        CorpusEntry(
            "pred1_nested_quant",
            "predicates1",
            _defs_1("active_for", "y", "T"),
            _always(_all("x", _imp(_p1("login_success", "x"), _ex("y", _p1("active_for", "y"))))),
            True,
            ["If a user logs in then there exists an active session for that user, always."],
        )
    )

    # 5) Boolean combination with guard
    defs_guard = _defs_0(["sensor_high", "manual_override", "alarm_on"], "T")
    entries.append(
        CorpusEntry(
            "guard_or_implies",
            "guards",
            defs_guard,
            _always(_imp(_or(_p0("sensor_high"), _p0("manual_override")), _p0("alarm_on"))),
            True,
            ["If sensor is high or manual override is on then the alarm turns on, always."],
        )
    )

    # 6) Generate families programmatically to reach a few hundred entries
    # Families: depth of nesting, combinations of all/ex, and/or, implications with negated guards
    idx = 0
    for depth in range(1, 6):  # 5 levels of nesting
        for a_and_b in [(True, True), (True, False), (False, True)]:
            a = "T" if a_and_b[0] else "F"
            b = "T" if a_and_b[1] else "F"
            phi = _and(a, b)
            psi = _or(a, b)
            chi = _imp(phi, psi)
            nest = chi
            for _ in range(depth - 1):
                nest = _always(nest)
            entries.append(
                CorpusEntry(
                    f"fam_base_{depth}_{idx}",
                    "family_base",
                    [],
                    nest,
                    True,
                    [f"Depth {depth} nested invariant over simple boolean implication."],
                )
            )
            idx += 1

    # Quantifier families with unary predicate stubs
    for n in range(1, 31):
        pname = f"p{n}"
        qname = f"q{n}"
        defs = [f"{pname}[0](x) := T.", f"{qname}[0](x,y) := T."]
        tau = _always(_all("x", _imp(_p1(pname, "x"), _ex("y", f"{qname}[0](x,y)"))))
        entries.append(
            CorpusEntry(
                f"fam_quant_{n}",
                "family_quant",
                defs,
                tau,
                True,
                [f"For every x, if {pname}(x) then there exists y such that {qname}(x,y), always."],
            )
        )

    # Mixed guard families
    for n in range(1, 31):
        a = f"a{n}"
        b = f"b{n}"
        c = f"c{n}"
        defs = _defs_0([a, b, c], "T")
        guard = _and(_p0(a), _neg(_p0(b)))
        tau = _always(_imp(guard, _p0(c)))
        entries.append(
            CorpusEntry(
                f"fam_guard_{n}",
                "family_guard",
                defs,
                tau,
                True,
                [f"If {a} and not {b} then {c}, always."],
            )
        )

    # Stream families
    for k in range(0, 5):
        tau = _always(_stream_eq("o1[t]", f"i1[t-{k}]" if k > 0 else "i1[t]"))
        prompt = "Output matches input" if k == 0 else f"Output equals input {k} step(s) earlier"
        entries.append(
            CorpusEntry(
                f"fam_stream_{k}",
                "family_stream",
                [],
                tau,
                True,
                [prompt + "."],
            )
        )

    # Truncate to requested size if needed
    if len(entries) > max_entries:
        entries = entries[:max_entries]
    return entries


def as_dicts(limit: int | None = None) -> List[Dict]:
    corpus = build_corpus()
    if limit is not None:
        corpus = corpus[:limit]
    return [
        {
            "id": e.id,
            "category": e.category,
            "defs": e.defs,
            "tau": e.tau,
            "expected_sat": e.expected_sat,
            "prompts": e.prompts,
        }
        for e in corpus
    ]


if __name__ == "__main__":
    import json
    data = as_dicts()
    print(json.dumps({"count": len(data)}, indent=2))


