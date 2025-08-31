# Autocomplete Improvements Plan (Non‑LLM, Offline‑First)

- Goals
  - Reduce ambiguity via intent cues (existential/universal/causal/guards).
  - Keep offline performance and determinism; optional small models.

- Generation
  - Grammar‑aware snippets: `ex x ( )`, `all x ( )`, `(cond) -> (act)`, `&&`, `||`, `!`.
  - Context cues: existence → prefer `ex`; universal → `all`; causal → `->`.

- Ranking (chain, feature‑flagged)
  - Default: rules → TF‑IDF.
  - Optional: fastText embeddings (cosine) → refine ordering.
  - Optional: MiniLM ONNX (int8) → best semantics when available.

- UI Integration
  - Clarifiers panel: temporal (invariant/atemporal) + quantifier preference (all/ex).
  - Ranked completion provider merges suggestions with the ranker.

- Testing
  - Unit/property: existential → `ex` tops; universal → `all`; causal → `->`.
  - Regression: request shaping applies clarifiers to backend.


