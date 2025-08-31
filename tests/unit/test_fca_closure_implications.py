from backend.unified.domain.fca import FormalContext, Implication


def test_closure_idempotence_and_monotonicity():
    attrs = ["a", "b", "c", "d"]
    # Objects have different attribute combinations
    objects = [
        ["a", "b"],
        ["a", "c"],
        ["b", "c", "d"],
    ]
    K = FormalContext(attrs, objects)
    A = {"a"}
    B = {"a", "b"}
    cA = K.closure(A)
    cAA = K.closure(cA)
    cB = K.closure(B)
    # idempotence: (A'')'' = A''
    assert cAA == cA
    # monotonicity: A ⊆ B ⇒ A'' ⊆ B''
    assert cA.issubset(cB)


def test_implication_generation_soundness_small():
    attrs = ["x", "y", "z"]
    # Design objects such that x implies y
    objects = [
        ["x", "y"],
        ["y"],
        ["z"],
    ]
    K = FormalContext(attrs, objects)
    impls = K.generate_implications_via_closure(max_premise_size=2)
    # check that for all (U->V) in impls, V ⊆ closure(U)
    for imp in impls:
        U = set(imp.premise)
        V = set(imp.conclusion)
        assert V.issubset(K.closure(U))


