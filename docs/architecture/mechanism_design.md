---
title: Tau Translator Mechanism Design (Internal)
---

## Overview
Tau Translator converts ambiguous English into precise Tau Controlled English (TCE) and Tau, and back to English. It prioritizes security, determinism, and truth-grounding against a native Tau interpreter.

## System Architecture
- Backend
  - Deterministic optimizer (PNF‑ILGO+):
    - FST normalization (operators/connectives)
    - Tier‑1 SRL‑style role extraction (condition, action, guard, negation, quantifiers, temporal)
    - Discrete intent lattice (FDL scaffold) for ambiguity scoring
    - Projection to TCE schema (always (...), quantifiers, guards)
    - Optional GS/NSO clean‑room IR → TCE pretty‑printer (feature‑flagged)
  - Normalization/tauization:
    - Grammar‑agnostic token normalization (and/or/->/all/ex/!)
    - Deterministic predicate synthesis (slugify from roles/phrases)
    - LMQL‑lite constraints and one‑shot repair for well‑formedness
    - Canonical parser/translator if available; simple translator fallback
    - Controlled‑English emission: “At all times, …” (no symbols)
  - Retrieval (RAG): lightweight knowledge pack for assist context
  - Ambiguity interface: score, facets, clarifying questions (for UI chips)
- Frontend
  - DeepL‑inspired two‑pane UI (Monaco input/output with tabs)
  - Local‑only mode; BYOK; chat side‑drawer
  - Planned: chips for clarifications and re‑translate with decisions
- Truth‑grounding
  - Tau REPL harness executes `sat always (...)` with generated stubs
  - Corpus‑based and prompt‑based E2E tests (Pytest)

## Data Contracts (APIs)
- POST `/llm/prompt-to-spec`
  - Request: `{ prompt: string, mode: "assist"|"generate", grammar_id?: string, grammar_version?: string, provider?: string, constraints?: { require_prefix?: string, require_closing_paren?: bool, forbid_colon?: bool, allowed_connectives?: string[] } }`
  - Response: `{ success: bool, tce?: string, tau?: string, reasons?: string[], provenance?: any, intent?: string, prompt_suggestions?: string[], nlp_analysis?: any, refined_prompt?: string, refined_options?: string[], ambiguity_score?: number, ambiguity_facets?: string[], clarifying_questions?: {question:string, options:string[]}[], chosen_cut?: any }`
- POST `/llm/spec-to-prompt`
  - Request: `{ spec_text: string, spec_type: "tce"|"tau" }`
  - Response: `{ success: bool, prompt_candidate?: string, explanation?: string, analysis?: any, verification?: any }`
- POST `/llm/chat`
  - Request: `{ messages: {role:"user"|"assistant"|"system", content:string}[] }`
  - Response: `{ reply: string, tce?: string, tau?: string, tool_calls?: any[] }`

## Normalization Rules (excerpt)
- Connectives: `and|AND|&& → and`; `or|OR|\|\| → or`; `implies|=>|⇒ → ->`
- Quantifiers: `forall|for all → all`; `exists|there exists → ex`
- Negation: `not|! → not`; English emission renders as “do not …”
- Literals: `true → T`, `false → F`
- Implication: `if X then Y → (X) -> (Y)`; also `when|whenever|after X, Y → (X) -> (Y)`
- Predicate synthesis: slugify head phrase → `predicate_name[0](x)`; default unary

Examples:
- “Never send data over the network.” → `always (all x (!send_over_network[0](x)))`
- “Every user must have a profile.” → `always (all x (user[0](x) -> has_profile[0](x)))`
- “There exists a session for each login.” → `always (all x (login[0](x) -> ex y (session_for[0](x,y))))`
- “If sensor is high or manual override is on then alarm turns on.” → `always (((sensor_high[0]() || manual_override[0]()) -> alarm_on[0]()))`

## Deterministic Predicate Synthesis
1) Extract roles (Tier‑1): action, condition, guard, negation, quantifiers, temporal
2) Slugify phrases to canonical identifiers (stop‑word removal, lowercase, underscores)
3) Choose arity (default unary) and introduce variables when quantifiers present
4) Compose formula by intent: invariant (optionally negated), causal (cond -> act), equivalence (two implications)
5) Apply guards as negative conditions, then wrap quantifiers and `always (...)`
6) Degeneracy guard: avoid collapsing to `always (T)` when roles/negation present; synthesize minimal predicate/quantifier instead

## Intent Lattice (FDL) and GS/NSO IR
- FDL bitset scaffold encodes: intent, guards, quantifiers, temporal irreducibles
- Constraint projection via bitmask (future: policy‑driven masks)
- GS/NSO clean‑room IR (feature‑flagged):
  - AST nodes: Var, At, Not, And, Or, Imply, Quant, Always
  - Builders from features, NNF/normalization, pretty‑printer to TCE‑like text

## Failure Modes & Mitigations
- Parser unavailable → fallback to simple translator or tau‑like acceptance path
- Unbalanced parentheses → normalization balances and whitelists tokens
- Ambiguous negation scope (“do not …”) → clarifying question chips
- Degenerate outputs (e.g., `always(T)`) → synthesize predicate with quantifier
- REPL SAT failures → stub predicates (True by default, False when negated)

## Testing Strategy
- Integration E2E (live API):
  - Assert TCE is controlled English (“At all times, …”; no symbols)
  - Assert Tau structure (always(...), balanced parens, logical tokens)
  - Run Tau SAT via native interpreter with auto‑stubs; pass if SAT (T)
- Corpus expansion:
  - Facets: negation scope; universal/existential; causal; guards; boolean coordination; temporal indices
  - Harder cases: numeric comparisons, chained implications, nested quantifiers
- Tools: `tools/generate_tau_corpus.py`, `tools/tau_runtime_harness.py`

## Deployment & Security
- Backend: Fly.io; health via 0.0.0.0:8080; CORS open to site origin
- Frontend: GitHub Pages with `.nojekyll`; CSP tuned for Monaco/workers
- Privacy: Local‑only mode and BYOK; store clarifications client‑side
- Licensing: Avoid bundling proprietary grammars; grammar packs are pluggable and versioned

## Metrics & Backlog
- Metrics (planned): ambiguity distribution, clarification rate, SAT pass rate
- Backlog:
  - Tier‑2 spaCy adapter (flagged)
  - GrammarProfile parameterization and drift CI
  - Version‑space clarification (FDL) with WSED reranker
  - UI chips wired to re‑translate with decisions

## Processing Flow
1) Prompt → FST normalize → Tier‑1 role extraction → Intent/ambiguity
2) Project to TCE (always (...); quantifiers/guards/negation handled)
3) Normalize to Tau tokens; synthesize predicate atoms; parse/translate
4) Emit Controlled‑English TCE, Tau, reasons, and clarifications
5) SAT‑check Tau against native interpreter; record result

## Deterministic Optimizer (PNF‑ILGO+)
- Inputs: prompt text, optional constraints
- Outputs: TCE, analysis (roles, quantifiers, negation, temporal), reasons, questions, ambiguity
- Guards: token whitelist, paren balancing, degenerate prevention (avoid `always(T)` for meaningful prompts)
- Flags: `TAU_OPTIMIZER_USE_FDL`, `TAU_OPTIMIZER_USE_GS`

## Normalization and Tauization
- Map phrases to Tau tokens: and/or/implication, quantifiers, negation, T/F
- Predicate synthesis: slugify head phrases; canonical arity defaults to unary
- Special handlers: common quantified/casual templates (e.g., session/login, user/profile)
- Controlled‑English emission: `_tce_to_english` renders “At all times, …”

## Ambiguity Handling
- Score from roles/intents presence
- Facets: intent, quantifiers, negation, guards, temporal
- Clarifying questions: generated deterministically; UI chips store answers client‑side

## Testing & Verification
- Integration tests call live API; enforce TCE English and Tau structure
- Tau harness defines predicate stubs (T by default; F under negation) and runs `sat` in native interpreter
- Corpus generation tools and optimizer comparison tooling

## Security & Licensing
- Client‑first; BYOK; local‑only mode available
- Clean‑room GS/NSO IR; avoid bundling proprietary grammars; grammar packs are pluggable

## Future Work
- Tier‑2 spaCy adapter (feature‑flagged)
- Full FDL projection with version‑space clarification and WSED reranker
- GrammarProfile parameterization and drift CI
- UI chips → feedback loop into optimizer


