## PNF‑ILGO+: Prompt Normal Form with Intent Lattice and Guarded Operators

Author: Dana Edwards

### Purpose
Transform ambiguous English prompts into precise Tau Controlled English (TCE) deterministically. PNF‑ILGO+ combines symbolic constraints with small learned/ranking components to minimize user burden while ensuring grammar validity and explainability.

### Problem Statement
Given an English prompt E, produce TCE S in normal form while minimizing the effort: minimize J(S,Q)=λ1·WSED(E→S)+λ2·|Q| subject to S∈Lang_TCE and constraints C(S)=true (syntax, scoping, operators). Q is the number of clarifying questions.

### Algorithm Overview
1) FST Normalization: canonicalize operators and conditionals (and/or/not, ->, all/ex).  
2) Typed Extraction: detect intent (invariant/causal/equivalence/temporal), condition, action, guards, quantifiers, time hints using deterministic patterns.  
3) Intent Lattice (ILGO): build a distributive lattice over (IntentType × GuardSet × QuantifierSet × TemporalIndex).  
4) Constraint Projection: compute greatest lower bound (GLB) under TCE constraints; guarantees schema compliance.  
5) Minimal‑Edit Synthesis: construct a short canonical TCE: `always ( … )`, adding guards/quantifiers/time index as needed.  
6) Ambiguity & Clarification (CEGC): estimate ambiguity from the version space; generate 1–3 high‑information questions when needed.  
7) Validation/Repair: enforce token whitelist, balance parens, normalize connectives; validate with canonical parser when available.

### Data Structures
- Features: {intent, condition, action, guards[], quantifiers[], temporal[]}  
- Lattice Node: (intent, guards, quants, timeIndex).  
- Constraints: {require_prefix, require_closing_paren, forbid_colon, allowed_connectives[]}.

### Weighted Structural Edit Distance (WSED)
Defined over operator trees. Edits and costs: normalize connectives (low), add guard (medium), add quantifier (medium), add time index (med‑high). Used for candidate selection and later reranking (Phase 2+).

### Version‑Space Clarification (Phase 2)
Maintain H⊆L consistent with E. Ask questions that maximize information gain by splitting H while minimizing cognitive cost. Stop when |H|=1 or Δscore<ε.

### ROP Contract
`optimize_prompt_to_tce(prompt, constraints) -> Result[OptimizerOutput]`  
returns Success with fields `{tce, intent, guards, quantifiers, temporal, reasons, analysis, questions, ambiguity}` or Failure with message.

### Implementation (Phase 1)
File: `backend/unified/domain/prompt_optimizer_pnf_ilgo.py`  
Steps implemented: FST normalization, typed extraction, projection, gating, ambiguity estimation, question generation.  
Integration: `/llm/prompt-to-spec` prefers optimizer output; still calls LLM for assist context and suggestions.

### Future Work
- Add operator‑tree WSED DP and on‑device reranker (TF.js).  
- Implement full version‑space clarifications and UI wiring.  
- Extend temporal reasoning and domain lexicon plugins.  
- Prove GLB existence for extended node sets; add property tests.

### Security & License
No embedded proprietary grammars. Deterministic gates and parser validation ensure safe outputs. BYOK supported via provider abstraction.


