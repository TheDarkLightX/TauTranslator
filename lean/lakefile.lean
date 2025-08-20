import Lake
open Lake DSL

package «tau_proofs» where
  -- Add configuration here if needed

require batteries from git
  "https://github.com/leanprover-community/batteries" @ "v4.22.0"

@[default_target]
lean_lib Tau


