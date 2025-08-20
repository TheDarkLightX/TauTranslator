#!/usr/bin/env python3
from __future__ import annotations

import random
import string
import timeit

from backend.unified.domain.normalization import gate_tokens as gate_slow
from backend.unified.domain.normalization_fast import gate_tokens_fast as gate_fast


def random_text(n: int) -> str:
    alphabet = string.ascii_letters + string.digits + " ()[],:!-|>&'"
    return "".join(random.choice(alphabet) for _ in range(n))


def bench(n=1000, size=80):
    samples = [random_text(size) for _ in range(n)]
    def run_slow():
        for s in samples:
            gate_slow(s)
    def run_fast():
        for s in samples:
            gate_fast(s)
    t1 = timeit.timeit(run_slow, number=1)
    t2 = timeit.timeit(run_fast, number=1)
    print(f"slow: {t1:.4f}s fast: {t2:.4f}s ratio={t2/max(t1,1e-9):.3f}")


if __name__ == '__main__':
    bench()


