import Tau.Certificates

/-!
Non‑trivial exemplar: map a finite Mealy‑style P to a tiny cognitive
Moore‑style C via witnesses f,g and verify robustness over a finite U.
-/

namespace Tau

inductive PIn
| a | b
deriving DecidableEq

inductive PState
| s0 | s1 | s2
deriving DecidableEq

open PIn PState

def P_tau : PState → PIn → PState
| s0, a => s1
| s0, b => s0
| s1, a => s1
| s1, b => s2
| s2, a => s1
| s2, b => s2

def P_Acc (_ : PState) (_ : PIn) : Prop := True

def P_sys : Finsys where
  S := PState
  I := PIn
  states := [s0, s1, s2]
  inputs := [a, b]
  tau := P_tau
  Acc := P_Acc

inductive CIn
| A | B
deriving DecidableEq

inductive CState
| start | seenA | yes
deriving DecidableEq

open CIn CState

def C_tau : CState → CIn → CState
| start, A => seenA
| start, B => start
| seenA, A => seenA
| seenA, B => yes
| yes,   A => seenA
| yes,   B => yes

def C_Acc (_ : CState) (_ : CIn) : Prop := True

def C_sys : Finsys where
  S := CState
  I := CIn
  states := [start, seenA, yes]
  inputs := [A, B]
  tau := C_tau
  Acc := C_Acc

-- Witnesses
def f_w : PState → CState
| s0 => start
| s1 => seenA
| s2 => yes

def g_w : PIn → CIn
| PIn.a => CIn.A
| PIn.b => CIn.B

def U_w (_s : PState) (_i : PIn) : Prop := True

theorem totalU_w : ∀ s i, U_w s i → P_sys.Acc s i := by intro; intro; intro; trivial

def cert_w : Cert P_sys C_sys :=
  { f := f_w, g := g_w, U := U_w, totalU := totalU_w }

-- Show robustness over enumerations
theorem robust_ok : checkRobustProp P_sys C_sys cert_w := by
  intro s hs i hi _
  cases s <;> cases i <;> simp [P_sys, C_sys, cert_w, f_w, g_w, P_tau, C_tau] at *

end Tau


