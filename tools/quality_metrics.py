#!/usr/bin/env python3
"""
Lightweight code quality metrics:
- Cyclomatic complexity/maintainability via radon (if installed)
- Shannon entropy of identifiers/tokens per function (AST-based)

Usage:
  python tools/quality_metrics.py backend/unified/domain/normalization.py
  python tools/quality_metrics.py backend
"""

from __future__ import annotations

import ast
import math
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple


def walk_py_files(path: str) -> List[str]:
    if os.path.isfile(path) and path.endswith('.py'):
        return [path]
    paths: List[str] = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith('.py'):
                paths.append(os.path.join(root, f))
    return sorted(paths)


def shannon_entropy(tokens: List[str]) -> float:
    if not tokens:
        return 0.0
    freq: Dict[str, int] = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    n = float(len(tokens))
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


_NAME_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass
class FuncEntropy:
    filename: str
    func: str
    lineno: int
    tokens: int
    entropy: float


def function_tokens(src: str, node: ast.AST) -> List[str]:
    if not hasattr(node, 'lineno') or not hasattr(node, 'end_lineno'):
        return []
    lines = src.splitlines()
    seg = "\n".join(lines[node.lineno - 1 : node.end_lineno])
    return _NAME_RE.findall(seg)


def analyze_entropy(path: str) -> List[FuncEntropy]:
    out: List[FuncEntropy] = []
    with open(path, 'r', encoding='utf-8') as fh:
        src = fh.read()
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            toks = function_tokens(src, n)
            ent = shannon_entropy(toks)
            out.append(FuncEntropy(path, n.name, getattr(n, 'lineno', 0), len(toks), ent))
    return sorted(out, key=lambda x: x.entropy, reverse=True)


def try_radon(paths: List[str]) -> None:
    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit
    except Exception:
        print("[info] radon not installed; skipping cyclomatic/MI. pip install radon")
        return
    for p in paths:
        try:
            with open(p, 'r', encoding='utf-8') as fh:
                src = fh.read()
            blocks = cc_visit(src)
            mi = mi_visit(src, multi=True)
            worst = sorted(blocks, key=lambda b: b.complexity, reverse=True)[:5]
            print(f"\n== {p} ==")
            print(f"Maintainability Index: {mi:.2f}")
            for b in worst:
                print(f"  CC {b.complexity:>3}  {b.name}  L{b.lineno}")
        except Exception as e:
            print(f"[warn] radon failed on {p}: {e}")


def main():
    target = sys.argv[1] if len(sys.argv) > 1 else 'backend'
    files = walk_py_files(target)
    # entropy
    ent_all: List[FuncEntropy] = []
    for f in files:
        ent_all.extend(analyze_entropy(f))
    print("Top functions by Shannon entropy (higher can indicate cognitive complexity):")
    for fe in ent_all[:10]:
        print(f"  {fe.filename}:{fe.lineno}  {fe.func}  tokens={fe.tokens}  H={fe.entropy:.2f}")
    # radon metrics
    try_radon(files)


if __name__ == '__main__':
    main()


