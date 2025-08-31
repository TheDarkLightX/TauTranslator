from __future__ import annotations

"""
Spec→Prompt (AST-driven) engine
================================

Deterministic, license-safe summarizer that converts Tau/TCE specs into
plain-English prompts and explanations using a lightweight AST built from
Tau-like expressions. No domain-specific hardcoding.

Public API:
- build_spec_to_prompt(spec_text: str, spec_type: str) -> dict
  Returns a dict with keys: explanation, prompt, analysis, verification.
"""

import re
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


# ---------- Minimal AST node definitions ----------

class Node:
    pass


@dataclass
class Predicate(Node):
    name: str
    args: List[str]


@dataclass
class Ref(Node):
    ident: str  # e.g., i0[t], o1[t-1]


@dataclass
class Not(Node):
    expr: Node


@dataclass
class BinOp(Node):
    op: str  # '->', '&&', '||'
    left: Node
    right: Node


@dataclass
class Quant(Node):
    kind: str  # 'all' or 'ex'
    var: str
    body: Node


@dataclass
class Rel(Node):
    left: Node
    op: str  # =, !=, <, <=, >, >=, interval ops folded as strings
    right: Node


# ---------- Parsing helpers (balanced top-level splits) ----------

def _strip_outer_parens(text: str) -> str:
    t = text.strip()
    if not (t.startswith("(") and t.endswith(")")):
        return t
    depth = 0
    for i, ch in enumerate(t):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and i < len(t) - 1:
            return t
    return t[1:-1].strip()


def _split_top(text: str, token: str) -> List[str]:
    out: List[str] = []
    buf: List[str] = []
    depth = 0
    i = 0
    L = len(text)
    while i < L:
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if depth == 0 and text.startswith(token, i):
            out.append("".join(buf).strip())
            buf = []
            i += len(token)
            continue
        buf.append(ch)
        i += 1
    out.append("".join(buf).strip())
    return out


# ---------- Expression parser for Tau-like WFF ----------

def parse_wff(expr: str) -> Node:
    # Normalize minimal punctuation and spacing
    t = _strip_outer_parens(expr)
    t = t.strip()
    # Strip trailing sentence punctuation
    t = re.sub(r"[\.;:]+\s*$", "", t)

    # Implication has lowest precedence
    parts = _split_top(t, "->")
    if len(parts) == 2:
        return BinOp("->", parse_wff(parts[0]), parse_wff(parts[1]))

    # OR
    parts_or = _split_top(t, "||")
    if len(parts_or) > 1:
        node = parse_wff(parts_or[0])
        for p in parts_or[1:]:
            node = BinOp("||", node, parse_wff(p))
        return node

    # AND
    parts_and = _split_top(t, "&&")
    if len(parts_and) > 1:
        node = parse_wff(parts_and[0])
        for p in parts_and[1:]:
            node = BinOp("&&", node, parse_wff(p))
        return node

    # Negation
    if t.startswith("!"):
        return Not(parse_wff(t[1:].strip()))

    # Quantifiers: all x (...), ex x (...)
    m_all = re.match(r"^all\s+([A-Za-z])\s*\((.*)\)$", t, flags=re.IGNORECASE | re.DOTALL)
    if m_all:
        return Quant("all", m_all.group(1), parse_wff(m_all.group(2)))
    m_ex = re.match(r"^ex\s+([A-Za-z])\s*\((.*)\)$", t, flags=re.IGNORECASE | re.DOTALL)
    if m_ex:
        return Quant("ex", m_ex.group(1), parse_wff(m_ex.group(2)))

    # Relational (simple forms) - tolerate spaces or no spaces
    for op in ["<=", ">=", "!=", "=", "<", ">"]:
        parts_rel = _split_top(t, op)
        if len(parts_rel) == 2:
            left = parts_rel[0].rstrip()
            right = parts_rel[1].lstrip()
            return Rel(_parse_atom(left), op, _parse_atom(right))

    # Atom
    return _parse_atom(t)


def _parse_atom(text: str) -> Node:
    s = text.strip()
    # Predicate name(args)
    m_pred = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)$", s)
    if m_pred:
        name = m_pred.group(1)
        args = [a.strip() for a in m_pred.group(2).split(",") if a.strip()]
        return Predicate(name=name, args=args)
    # Time-indexed reference like o1[t], i0[t-1]
    m_ref = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\[(.*?)\]", s)
    if m_ref:
        return Ref(ident=s)
    # Bare identifier
    return Predicate(name=s, args=[])


# ---------- English emission from AST ----------

def _humanize_ident(identifier: str) -> str:
    # Time index forms like o1[t-1]
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\[(.*)\]$", identifier)
    if m:
        base = re.sub(r"_+", " ", m.group(1)).strip()
        idx = m.group(2)
        return f"{base} at time {idx}"
    return re.sub(r"_+", " ", identifier).strip()


def to_english(node: Node) -> str:
    if isinstance(node, BinOp):
        l = to_english(node.left)
        r = to_english(node.right)
        if node.op == "->":
            return f"if {l} then {r}"
        if node.op == "&&":
            return f"{l} and {r}"
        if node.op == "||":
            return f"{l} or {r}"
        return f"{l} {node.op} {r}"
    if isinstance(node, Not):
        inner = to_english(node.expr)
        return f"do not {inner}"
    if isinstance(node, Quant):
        inner = to_english(node.body)
        return (f"for every {node.var}, {inner}" if node.kind == "all"
                else f"there exists {node.var} such that {inner}")
    if isinstance(node, Predicate):
        return _humanize_ident(node.name)
    if isinstance(node, Ref):
        return _humanize_ident(node.ident)
    if isinstance(node, Rel):
        return f"{to_english(node.left)} {node.op} {to_english(node.right)}"
    return str(node)


# ---------- Multiline TAU summarizer (declarations + r(...)) ----------

def _extract_r_block(joined: str) -> str:
    r_idx = re.search(r"\br\s*\(", joined)
    if not r_idx:
        return ""
    start = joined.find("(", r_idx.start())
    depth = 0
    for i in range(start, len(joined)):
        ch = joined[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return joined[start + 1:i]
    return ""


def _summarize_multiline_tau(text: str) -> Tuple[str, str, dict, dict]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    non_comment = [ln for ln in lines if not re.match(r"^\s*#", ln)]
    decl_inputs: List[str] = []
    decl_outputs: List[str] = []
    helpers: List[str] = []
    title: Optional[str] = None
    for ln in lines:
        m_title = re.match(r"^\s*#\s*(.+)$", ln)
        if m_title:
            title = m_title.group(1).strip()
            break
    for ln in non_comment:
        m_sbf = re.match(r"^\s*sbf\s+([A-Za-z_][\w]*)\s*=", ln)
        if m_sbf:
            name = m_sbf.group(1)
            if name.lower().startswith("i"):
                decl_inputs.append(name)
            elif name.lower().startswith("o"):
                decl_outputs.append(name)
            continue
        m_help = re.match(r"^\s*([A-Za-z_][\w]*)\s*\([^)]*\)\s*: =|^\s*([A-Za-z_][\w]*)\s*:=", ln.replace(" ", ""))
        if m_help:
            h = m_help.group(1) or m_help.group(2)
            if h:
                helpers.append(h)
    joined = "\n".join(non_comment)
    r_block = _extract_r_block(joined)
    eq_count = 0
    outputs_in_eq: List[str] = []
    uses_prev_time = False
    if r_block:
        uses_prev_time = ("[t-1]" in r_block)
        parts = re.split(r"&&\s*\n?|\)\s*&&\s*\(", r_block)
        for seg in parts:
            m_eq = re.search(r"^\s*([A-Za-z_][\w]*)\s*\[t\]\s*=", seg)
            if m_eq:
                eq_count += 1
                outputs_in_eq.append(m_eq.group(1))

    bullets: List[str] = []
    if title:
        bullets.append(f"Title: {title}.")
    if decl_inputs:
        bullets.append(f"Inputs: {', '.join(sorted(set(decl_inputs)))}.")
    if decl_outputs:
        bullets.append(f"Outputs: {', '.join(sorted(set(decl_outputs)))}.")
    if helpers:
        bullets.append(f"Helper predicates: {', '.join(sorted(set(helpers)))}.")
    if r_block:
        bullets.append(
            f"Transition relations: {eq_count} output equations in r(...). Uses previous time index: {'yes' if uses_prev_time else 'no'}."
        )
    bullets.append("Boolean state machine over time: outputs at [t] depend on current inputs and previous outputs [t-1].")
    explanation = " ".join(bullets)
    prompt = (
        f"State machine with {eq_count} temporal equations; outputs at t use inputs and possibly previous outputs."
    )
    analysis = {
        "temporal": ("[t]" in text) or ("always" in text.lower()),
        "implication": ("->" in text),
        "quantifiers": [],
        "time_indices": sorted(list(set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t(?:-1)?\]", text)))),
        "sections": [s for s in ["declarations", "helpers", "relations"] if (decl_inputs or decl_outputs) or helpers or r_block],
        "equations": eq_count,
        "uses_prev_time": uses_prev_time,
        "helpers_present": {"count": len(set(helpers))},
    }
    verification = {
        "equations": eq_count,
        "uses_prev_time": uses_prev_time,
        "time_indices_count": len(analysis.get("time_indices", [])),
    }
    return explanation, prompt, analysis, verification


# ---------- Public Builder ----------

def build_spec_to_prompt(spec_text: str, spec_type: str) -> dict:
    text = spec_text.strip()
    # Multiline Tau-like program: use block summarizer
    if "\n" in text:
        explanation, prompt, analysis, verification = _summarize_multiline_tau(text)
        return {
            "explanation": explanation,
            "prompt": prompt,
            "analysis": analysis,
            "verification": verification,
        }

    # Single-line: attempt to parse always(...) and inner WFF
    is_always = False
    inner = text
    # Support both always ( ... ) and bare always ...
    m_always_paren = re.match(r"^\s*always\s*\((.*)\)\s*$", text, flags=re.IGNORECASE | re.DOTALL)
    if m_always_paren:
        inner = m_always_paren.group(1).strip()
        is_always = True
    else:
        m_always_bare = re.match(r"^\s*always\s+(.+)$", text, flags=re.IGNORECASE | re.DOTALL)
        if m_always_bare:
            inner = m_always_bare.group(1).strip()
            is_always = True
    # Normalize prime (next) notation often used in Tau docs: o1[t]' => o1[t+1]
    inner = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*t\s*\]\s*'", r"\\1[t+1]", inner)
    inner = re.sub(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[\s*t\s*-\s*1\s*\]\s*'", r"\\1[t]", inner)
    # Strip trailing punctuation in inner too
    inner = re.sub(r"[\.;:]+\s*$", "", inner)
    try:
        ast = parse_wff(inner)
        phrase = to_english(ast)
        sentence = (f"At all times, {phrase}" if is_always else phrase)
        sentence = sentence[0].upper() + sentence[1:]
        if not sentence.endswith("."):
            sentence += "."
        explanation = sentence
        prompt = sentence
        analysis = {
            "temporal": is_always or bool(re.search(r"\[t(?:-1)?\]", text)),
            "implication": "->" in inner,
            "quantifiers": [q for q in ["all", "ex"] if re.search(fr"\b{q}\b", inner)],
            "time_indices": list(set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t(?:-1)?\]", inner))),
        }
        verification = {"parsed": True}
        return {
            "explanation": explanation,
            "prompt": prompt,
            "analysis": analysis,
            "verification": verification,
        }
    except Exception:
        # Fallback: minimal humanization
        human = (
            inner.replace("->", " implies ")
                 .replace("!", "not ")
                 .replace("&&", " and ")
                 .replace("||", " or ")
        )
        human = re.sub(r"_+", " ", human)
        if is_always:
            human = f"At all times, {human}"
        if not human.endswith("."):
            human += "."
        return {
            "explanation": human,
            "prompt": human,
            "analysis": {
                "temporal": is_always,
                "implication": " implies " in human,
                "quantifiers": [q for q in ["all", "ex"] if re.search(fr"\b{q}\b", inner)],
                "time_indices": list(set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[t(?:-1)?\]", inner))),
            },
            "verification": {"parsed": False},
        }


