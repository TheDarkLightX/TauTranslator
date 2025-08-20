/-!
Finite certificate checker (scaffold)

We avoid external finite set dependencies by carrying explicit
enumerations for states and inputs. The checker is expressed as a
proposition over these enumerations, suitable for computable instances
or interactive proofs.
-/

universe u v

namespace Tau

structure Finsys where
  S : Type u
  I : Type v
  states : List S
  inputs : List I
  tau : S → I → S
  Acc : S → I → Prop

structure Cert (P C : Finsys) where
  f : P.S → C.S
  g : P.I → C.I
  U : P.S → P.I → Prop
  totalU : ∀ s i, U s i → P.Acc s i

/-- Propositional checker over explicit finite enumerations. -/
def checkRobustProp (P C : Finsys) (c : Cert P C) : Prop :=
  ∀ s, s ∈ P.states → ∀ i, i ∈ P.inputs → c.U s i →
    c.f (P.tau s i) = C.tau (c.f s) (c.g i)

end Tau


