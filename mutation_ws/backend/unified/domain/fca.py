from __future__ import annotations

"""
Formal Concept Analysis (FCA)
=============================

Deterministic FCA utilities for computing closures, concept intents/extents,
and implications from a formal context. No heuristics, no placeholders.

Definitions (finite case):
- Formal context K = (O, A, I) where O is a finite set of objects, A a finite
  set of attributes, and I ⊆ O×A is the incidence relation "object o has attr a".
- For B ⊆ A, extent B' = { o ∈ O | ∀a∈B: (o,a)∈I }.
- For X ⊆ O, intent X' = { a ∈ A | ∀o∈X: (o,a)∈I }.
- Closure on attributes is c(B) = B'' (apply derivation twice).
- Implication U → V holds in K iff V ⊆ c(U).

This module implements:
- FormalContext: holds A, O, and I (as attribute names and per-object attr sets)
- closure(B), extent(B), intent(Oidx)
- generate_implications_via_closure: exact implications discovered by scanning
  attribute subsets up to a max premise size and removing redundant ones via
  closure under the evolving basis.

Note: For large |A|, scanning all subsets is exponential. In this codebase the
attribute vocabulary is compact (facets), making this feasible and exact.
"""

from dataclasses import dataclass
from typing import List, Set, Dict, Iterable, Tuple
import itertools


@dataclass(frozen=True)
class Implication:
    premise: frozenset[str]
    conclusion: frozenset[str]

    def __str__(self) -> str:
        lhs = ", ".join(sorted(self.premise)) or "∅"
        rhs = ", ".join(sorted(self.conclusion)) or "∅"
        return f"{lhs} -> {rhs}"


class FormalContext:
    def __init__(self, attributes: List[str], objects: List[Iterable[str]]):
        self.attributes: List[str] = list(dict.fromkeys(attributes))
        # map object to attribute set limited to known attributes for safety
        attr_set = set(self.attributes)
        self.objects: List[frozenset[str]] = [
            frozenset(a for a in obj if a in attr_set) for obj in objects
        ]
        # quick index
        self._A: Set[str] = set(self.attributes)

    # ----- FCA derivation operators -----
    def extent(self, attrs: Iterable[str]) -> Set[int]:
        B = set(attrs)
        if not B:
            return set(range(len(self.objects)))
        idxs: Set[int] = set()
        for i, obj_attrs in enumerate(self.objects):
            if B.issubset(obj_attrs):
                idxs.add(i)
        return idxs

    def intent(self, objs: Iterable[int]) -> Set[str]:
        idxs = list(objs)
        if not idxs:
            return set(self.attributes)  # intent of empty extent is A
        inter = set(self.objects[idxs[0]])
        for i in idxs[1:]:
            inter &= self.objects[i]
        return inter

    def closure(self, attrs: Iterable[str]) -> Set[str]:
        return self.intent(self.extent(attrs))

    # ----- Implication basis via closure enumeration -----
    @staticmethod
    def _apply_implications(base: List[Implication], premise: Set[str]) -> Set[str]:
        closure = set(premise)
        changed = True
        while changed:
            changed = False
            for imp in base:
                if imp.premise.issubset(closure) and not imp.conclusion.issubset(closure):
                    closure |= imp.conclusion
                    changed = True
        return closure

    def generate_implications_via_closure(
        self,
        max_premise_size: int | None = None,
    ) -> List[Implication]:
        """Compute a sound (not necessarily minimal) implication base.

        Strategy: enumerate attribute subsets up to max_premise_size (or all if None),
        compute formal closure c(X) = X''; if c(X) > X then X -> c(X)\X is an
        implication. Add to a growing base only if it is not already entailed by
        existing implications (test via base-closure of X).
        """
        A = self.attributes
        n = len(A)
        size_limit = n if max_premise_size is None else max_premise_size
        base: List[Implication] = []
        for r in range(0, size_limit + 1):
            for combo in itertools.combinations(A, r):
                X = set(combo)
                # closure in context
                cl = self.closure(X)
                if cl.issubset(X):
                    continue
                # check if entailed by base
                cl_base = FormalContext._apply_implications(base, X)
                if set(cl).issubset(cl_base):
                    continue
                # add reduced conclusion
                concl = set(cl) - X
                if concl:
                    base.append(Implication(frozenset(X), frozenset(concl)))
        # Optional: simple redundancy elimination pass
        pruned: List[Implication] = []
        for i, imp in enumerate(base):
            tmp = base[:i] + base[i+1:]
            if set(FormalContext._apply_implications(tmp, imp.premise)).issuperset(imp.conclusion | imp.premise):
                # redundant
                continue
            pruned.append(imp)
        return pruned


