/-!
Formalization: Trivial pancomputationalism under an implementation-as-homomorphism definition.

Every system implements itself via identity maps, so ∀ P, ∃ C, Implements P C holds by choosing C = P.
This captures the trivial case; nontrivial variants require stronger constraints.
-/

universe u₁ v₁ u₂ v₂ u v

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
  refine ⟨P, pancomputational_self P⟩


