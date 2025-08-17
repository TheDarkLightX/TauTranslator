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


