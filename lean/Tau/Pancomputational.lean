/-!
# Pancomputationalism (trivial case)

We formalize a simple notion of implementation as a homomorphism that preserves
state transitions (with an accessibility side-condition), and show that every
system implements itself by identity functions. Consequently, for any system `P`
there exists a system `C` such that `Implements P C` by taking `C = P`.

This captures a trivial pancomputationalism theorem; stronger results require
additional constraints (e.g., computational type, counterfactual robustness,
or restrictions on admissible witnesses).
-/

universe u₁ v₁ u₂ v₂ u v

namespace Tau

structure System (S : Type u) (I : Type v) where
  tau : S → I → S
  Acc : S → I → Prop

def Implements {S₁ : Type u₁} {I₁ : Type v₁} {S₂ : Type u₂} {I₂ : Type v₂}
  (P : System S₁ I₁) (C : System S₂ I₂) : Prop :=
  ∃ (f : S₁ → S₂) (g : I₁ → I₂),
    ∀ (s : S₁) (i : I₁), P.Acc s i → f (P.tau s i) = C.tau (f s) (g i)

theorem pancomputational_self {S : Type u} {I : Type v}
  (P : System S I) : Implements P P := by
  refine ⟨id, id, ?h⟩
  intro s i _h
  rfl

theorem pancomputational {S : Type u} {I : Type v}
  (P : System S I) : ∃ (C : System S I), Implements P C := by
  exact ⟨P, pancomputational_self P⟩

end Tau


