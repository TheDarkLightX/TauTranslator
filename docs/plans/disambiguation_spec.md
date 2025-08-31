# Disambiguation Engine Design (Intent Lattice + Ranker + NLI + EL)

## Objectives
- Deterministically reduce ambiguity before formalization
- Default to offline operation; gate heavier components with feature flags
- Map user clarifications (lattice cuts) directly to concrete constraints

## Scope and definitions
- Atemporal: single-situation statement; do not wrap with `always (...)`
- Invariant: rule that should hold over time; wrap with `always (...)`
- Quantifiers: `all` vs `ex`. Use explicit user text if present; otherwise infer or apply preference

## High-level pipeline
1. Pre-normalize and gate
   - Sanitize tokens, balance parentheses, trim
   - Temporal gating: infer atemporal/invariant; respect UI `temporal_mode`
   - Heuristic intent cues: existential/universal/causal/guards/negation
2. Candidate synthesis
   - Deterministic forms: implication, quantified variants, atemporal counterparts
   - Keep inner form neutral; only add `always` if temporal
3. Ranking (semantic + rules)
   - Rule features: existence -> `ex`, universal -> `all`, causal -> `->`, penalize premature `always`
   - TF-IDF cosine (default, offline)
   - Optional fastText-lite n-gram similarity (offline)
   - Optional MiniLM-ONNX cosine (feature-flagged)
4. NLI rerank (feature-flagged)
   - Premise = prompt; hypotheses = Englishified TCE candidates
   - Score = p(entailment) - p(contradiction); choose argmax
   - Fail closed if model missing
5. Clarifier loop (UI)
   - Temporal chip -> `temporal_mode`
   - Quantifier chip -> `constraints.prefer_quantifier`
   - Entity hints (if EL enabled) bias options (non-blocking)
6. Formal translation
   - Canonical parser/translator; fallback simple translator with acceptance normalization

## Temporal inference
- Invariant keywords: "always", "whenever", "must always", "never" (as invariant with negation)
- Atemporal cues: "there exists", "exists", "some", "at least one"
- Default: atemporal unless explicit temporal cue or UI selects Invariant

## Quantifier determination
- Detect explicit quantifiers in user text; if present, keep them
- If none: compute `(choice, reason)` using heuristics
  - Universal cues: "for all", "for each", "every"
  - Existential cues: "there exists", "exists", "some"
- If still None: apply `constraints.prefer_quantifier` when provided; record reason

## Candidate generation
- Start from neutral inner predicate(s)
- Generate: atemporal, `all` form, `ex` form, causal `A -> B` when guards detected
- Do not duplicate `always` if inner already temporal

## Ranking modes (offline-first)
- `rules`: rule-only scoring
- `tfidf`: cosine on bag-of-words vectors
- `rules+tfidf` (default): linear blend
- `fasttext`: n-gram/hashed subword vectors (lite)
- `rules+fasttext`: blend
- (optional) `minilm`: ONNX embeddings for cosine

## NLI reranker (optional)
- Flags: `TAU_ENABLE_NLI=1`, `TAU_NLI_MODEL=/path/to/model.onnx`
- Inputs: top-K candidates from ranker
- Output: best-scoring candidate; add reason with NLI scores
- Failure: if model missing/unloadable, skip and proceed

## Entity linking hook (optional)
- Flag: `TAU_ENABLE_REFINED=1`
- Map nouns/NPs to canonical predicate names via dictionary or lightweight linker
- Provide suggestions to predicate constructor; never force

## UI integration
- Clarifiers panel: Temporal (auto/invariant/atemporal), Quantifier (none/all/ex)
- Ranked suggestions list with labels: invariant/causal/quantified
- Reasons and clarifying questions shown in a sidebar
- Keyboard shortcuts: Ctrl+Enter translate, Alt+1/2/3 pane focus, ESC cancel
- Resizable panes; persist layout in local storage
- Flags surfaced: disable chips when features unavailable; show tooltips

## Feature flags
- Ranker mode: `VITE_TAU_RANKER_MODE=rules|tfidf|rules+tfidf|fasttext|rules+fasttext|minilm`
- NLI: `TAU_ENABLE_NLI=1`, `TAU_NLI_MODEL` path (default off)
- Entity Linking: `TAU_ENABLE_REFINED=1` (default off)

## Testing strategy (TDD)
- Unit/property
  - Atemporal prompts do not get `always` and English lacks "At all times,"
  - Universal vs existential heuristics steer quantifier when none present
  - `constraints.prefer_quantifier` applies only if quantifier missing; reason recorded
  - Ranker ordering: existential > universal for existential prompts; causal first for "if...then"
- Regression
  - NLI disabled: no-op; outputs unchanged apart from reasons
  - NLI enabled w/o model: fail closed; no crash
  - EL disabled: manual mapping path still passes

## Metrics / KPIs
- Ambiguity reduction: % prompts resolved without manual clarifiers
- Accuracy: agreement with gold intents (dev set)
- Latency budgets (CPU-only): TF-IDF < 10 ms; fastText-lite < 25 ms; MiniLM-ONNX < 80 ms
- Test coverage increase across llm endpoints and ranker

## Failure modes and fallbacks
- Missing models: continue with deterministic path
- Parse failure: return sanitized TCE and reasons; never crash
- Duplicate temporal wrappers: strip outer `always` when `atemporal`

## Security and privacy
- Offline by default; no data leaves device unless explicitly enabled
- Local models only unless BYOK configured; clearly surface remote calls
