import Tau.Pancomputational
import Tau.NonTrivial

/-!
Programmability schema: if a subsystem can be made to robustly
implement a target computation (via suitable boundary/initial
conditions), then we obtain a non‑trivial implementation provided
there exist non‑degenerate endomorphisms on the physical side.
-/

universe u₁ v₁ u₂ v₂

namespace Tau

/-- Existence of robust witnesses for P implementing C over U. -/
def Programmable
  {S₁ : Type u₁} {I₁ : Type v₁} {S₂ : Type u₂} {I₂ : Type v₂}
  (P : System S₁ I₁) (C : System S₂ I₂)
  (U : S₁ → I₁ → Prop) (hU : ∀ s i, U s i → P.Acc s i) : Prop :=
  ∃ (f : S₁ → S₂) (g : I₁ → I₂), RobustImplements P C U hU f g

/-- From programmability plus any non‑degeneracy witnesses, we derive
non‑trivial implementation. -/
theorem implementsNonTrivial_of_programmable
  {S₁ : Type u₁} {I₁ : Type v₁} {S₂ : Type u₂} {I₂ : Type v₂}
  (P : System S₁ I₁) (C : System S₂ I₂)
  (U : S₁ → I₁ → Prop) (hU : ∀ s i, U s i → P.Acc s i)
  (hp : Programmable P C U hU)
  (nd : ∃ (φ : S₁ → S₁) (γ : I₁ → I₁), NonDegenerate φ γ)
  : ImplementsNonTrivial P C U hU := by
  rcases hp with ⟨f, g, hrob⟩
  rcases nd with ⟨φ, γ, hnd⟩
  refine ⟨f, g, hrob, ?_⟩
  exact ⟨φ, γ, hnd⟩

/-- If the physical carriers have at least two distinct elements each,
we can synthesize non‑degenerate endomorphisms by swapping two points. -/
theorem existsNonDegenerate_of_two
  {S₁ : Type u₁} {I₁ : Type v₁}
  [DecidableEq S₁] [DecidableEq I₁]
  (Hs : ∃ s₁ s₂ : S₁, s₁ ≠ s₂)
  (Hi : ∃ i₁ i₂ : I₁, i₁ ≠ i₂)
  : ∃ (φ : S₁ → S₁) (γ : I₁ → I₁), NonDegenerate φ γ := by
  rcases Hs with ⟨s₁, s₂, hs⟩
  rcases Hi with ⟨i₁, i₂, hi⟩
  let φ : S₁ → S₁ := fun x => if x = s₁ then s₂ else if x = s₂ then s₁ else x
  let γ : I₁ → I₁ := fun x => if x = i₁ then i₂ else if x = i₂ then i₁ else x
  have hφs1 : φ s₁ = s₂ := by simp [φ]
  have hφs2 : φ s₂ = s₁ := by simp [φ]
  have hφ_diff : φ s₁ ≠ φ s₂ := by
    intro hfeq
    have : s₂ = s₁ := by simpa [hφs1, hφs2] using hfeq
    exact hs this.symm
  have hγi1 : γ i₁ = i₂ := by simp [γ]
  have hγi2 : γ i₂ = i₁ := by simp [γ]
  have hγ_diff : γ i₁ ≠ γ i₂ := by
    intro hfeq
    have : i₂ = i₁ := by simpa [hγi1, hγi2] using hfeq
    exact hi this.symm
  have not_both_id : ¬ ((∀ s, φ s = s) ∧ (∀ i, γ i = i)) := by
    intro h
    have hφ := h.left
    have hφs1' : φ s₁ = s₁ := hφ s₁
    -- but φ s₁ = s₂, contradiction with s₁ ≠ s₂
    have : s₂ = s₁ := by simpa [hφs1] using hφs1'
    exact hs this.symm
  refine ⟨φ, γ, And.intro not_both_id (And.intro ?h1 ?h2)⟩
  · exact ⟨s₁, s₂, hφ_diff⟩
  · exact ⟨i₁, i₂, hγ_diff⟩

/-- Corollary: with two‑element lower bounds and programmability,
we obtain non‑trivial implementation constructively. -/
theorem implementsNonTrivial_of_programmable_two
  {S₁ : Type u₁} {I₁ : Type v₁} {S₂ : Type u₂} {I₂ : Type v₂}
  [DecidableEq S₁] [DecidableEq I₁]
  (P : System S₁ I₁) (C : System S₂ I₂)
  (U : S₁ → I₁ → Prop) (hU : ∀ s i, U s i → P.Acc s i)
  (hp : Programmable P C U hU)
  (Hs : ∃ s₁ s₂ : S₁, s₁ ≠ s₂)
  (Hi : ∃ i₁ i₂ : I₁, i₁ ≠ i₂)
  : ImplementsNonTrivial P C U hU := by
  have ⟨φ, γ, hnd⟩ := existsNonDegenerate_of_two (S₁:=S₁) (I₁:=I₁) Hs Hi
  exact implementsNonTrivial_of_programmable P C U hU hp ⟨φ, γ, hnd⟩

end Tau


