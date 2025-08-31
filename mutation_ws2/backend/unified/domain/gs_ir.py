from __future__ import annotations

"""
GS/NSO-inspired semantic IR (clean-room).

Goal: Represent controlled invariants (always (...)) with guards, quantifiers,
temporal indices, and logical operators as a small, typed AST. Provide simple
normalization (NNF-ish) and pretty-print to a TCE-like surface without using
any IDNI implementation artifacts.
"""

from dataclasses import dataclass
from typing import List, Optional, Union


# === AST nodes ===


class Node:  # marker
    pass


@dataclass(frozen=True)
class Var(Node):
    name: str


@dataclass(frozen=True)
class At(Node):  # temporal reference: name@[offset]
    term: Var
    offset: int  # 0 for t, -1 for t-1, +1 for t+1


@dataclass(frozen=True)
class Not(Node):
    child: Node


@dataclass(frozen=True)
class And(Node):
    args: List[Node]


@dataclass(frozen=True)
class Or(Node):
    args: List[Node]


@dataclass(frozen=True)
class Imply(Node):
    lhs: Node
    rhs: Node


@dataclass(frozen=True)
class Quant(Node):
    kind: str  # 'all' | 'ex'
    var: str
    body: Node


@dataclass(frozen=True)
class Always(Node):
    body: Node


# === Builders ===


def var(name: str) -> Var:
    return Var(name=name)


def at(name: str, offset: int = 0) -> At:
    return At(term=Var(name), offset=offset)


def conj(*nodes: Node) -> Node:
    flat: List[Node] = []
    for n in nodes:
        if isinstance(n, And):
            flat.extend(n.args)
        else:
            flat.append(n)
    if len(flat) == 1:
        return flat[0]
    return And(args=flat)


def disj(*nodes: Node) -> Node:
    flat: List[Node] = []
    for n in nodes:
        if isinstance(n, Or):
            flat.extend(n.args)
        else:
            flat.append(n)
    if len(flat) == 1:
        return flat[0]
    return Or(args=flat)


# === Normalization ===


def to_nnf(n: Node) -> Node:
    # eliminate implication, push not inward (limited)
    if isinstance(n, Imply):
        return to_nnf(disj(Not(n.lhs), n.rhs))
    if isinstance(n, Not):
        c = n.child
        if isinstance(c, Not):
            return to_nnf(c.child)
        if isinstance(c, And):
            return disj(*[to_nnf(Not(a)) for a in c.args])
        if isinstance(c, Or):
            return conj(*[to_nnf(Not(a)) for a in c.args])
        # leave Not on atoms/quantified bodies
        return Not(to_nnf(c))
    if isinstance(n, And):
        return conj(*[to_nnf(a) for a in n.args])
    if isinstance(n, Or):
        return disj(*[to_nnf(a) for a in n.args])
    if isinstance(n, Quant):
        return Quant(kind=n.kind, var=n.var, body=to_nnf(n.body))
    if isinstance(n, Always):
        return Always(body=to_nnf(n.body))
    return n


# === Pretty-print to TCE-like text (clean-room) ===


def _pp(n: Node) -> str:
    if isinstance(n, Var):
        return n.name
    if isinstance(n, At):
        if n.offset == 0:
            return f"{n.term.name}[t]"
        if n.offset > 0:
            return f"{n.term.name}[t+{n.offset}]"
        return f"{n.term.name}[t{n.offset}]"  # offset negative prints as t-1, t-2
    if isinstance(n, Not):
        return f"not {_pp(n.child)}"
    if isinstance(n, And):
        return " and ".join(f"({_pp(a)})" if isinstance(a, (Or, Imply)) else _pp(a) for a in n.args)
    if isinstance(n, Or):
        return " or ".join(f"({_pp(a)})" if isinstance(a, (And, Imply)) else _pp(a) for a in n.args)
    if isinstance(n, Imply):
        return f"{_pp(n.lhs)} -> {_pp(n.rhs)}"
    if isinstance(n, Quant):
        return f"{n.kind} {n.var} ({_pp(n.body)})"
    if isinstance(n, Always):
        return f"always ({_pp(n.body)})"
    return "?"


def to_tce(n: Node) -> str:
    return _pp(n)


# === Feature mapping helper ===


def _contains_imply(n: Node) -> bool:
    if isinstance(n, Imply):
        return True
    if isinstance(n, (And, Or)):
        return any(_contains_imply(a) for a in (n.args if isinstance(n, (And, Or)) else []))
    if isinstance(n, Quant):
        return _contains_imply(n.body)
    if isinstance(n, Not):
        return _contains_imply(n.child)
    if isinstance(n, Always):
        return _contains_imply(n.body)
    return False


def build_from_features(intent: Optional[str], condition: Optional[str], action: Optional[str], guards: List[str], quantifiers: List[str], temporal: List[str]) -> Always:
    # condition/action as Vars (no parsing of complex expressions here)
    cond_node: Optional[Node] = var(condition) if condition else None
    act_node: Optional[Node] = var(action) if action else None
    # apply guards as negative preconditions
    gnode: Optional[Node] = None
    if guards:
        gnode = conj(*[Not(var(g)) for g in guards])
    body: Node
    if intent == "causal" and cond_node and act_node:
        lhs = cond_node if gnode is None else conj(cond_node, gnode)
        body = Imply(lhs, act_node)
    elif act_node is not None:
        body = act_node
    elif cond_node is not None:
        body = cond_node
    else:
        body = Var("true")
    # quantifiers wrap outermost body
    for q in quantifiers:
        if q.startswith("all"):
            body = Quant(kind="all", var="x", body=body)
        elif q.startswith("ex"):
            body = Quant(kind="ex", var="x", body=body)
    # Keep implication for pretty-printing arrow even under Quant; else push to nnf
    return Always(body=body if _contains_imply(body) else to_nnf(body))


