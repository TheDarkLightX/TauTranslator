# Tau Translator Codebase Complexity and Design Analysis

## Context and Goals
The Tau Translator has evolved into a sophisticated service for turning free‑form English into formal Temporal Logic Clause Expressions (TCE) and then into Tau specifications. Recent commits have refactored the code following SOLID principles and introduced atemporal support, an NLI re‑ranker, and hooks for entity linking. This document analyses the algorithmic and design complexity of the current backend and UI, identifies design patterns, and proposes strategies to reduce cyclomatic and cognitive complexity while improving maintainability and documentation.

## Key components analysed
- Backend API: `backend/unified/api/llm_endpoints.py` orchestrates pack retrieval, deterministic optimisation, LM prompting, temporality inference, sanitisation, optional NLI reranking, entity linking, and multiline handling.
- Disambiguation services: `infer_temporal_mode`, `choose_quantifier`, `sanitize_to_tce`, `get_nli_reranker` encapsulate heuristics and optional modules.
- UI: SvelteKit `+page.svelte` manages CodeMirror editors, requests, and presentation.

## Algorithmic analysis (high-level pipeline)
1. Grammar pack retrieval and caching
2. Deterministic optimisation (PNF‑ILGO)
3. Provider generation (with temporal guide)
4. Sanitisation and heuristics
5. Candidate reranking (optional NLI)
6. Entity linking (dictionary or ReFinED)
7. Multiline handling

## Complexity hot spots
1. Large monolithic `prompt_to_spec`
2. Heuristic sanitisation
3. NLI reranker branching
4. Phrase→predicate mapping sprawl
5. UI page mixing state + IO + rendering

## Design patterns observed
- Caching (Singleton-like caches)
- Factory/Provider
- Strategy (optimisers/spec strategies)
- Builder (knowledge packs)
- Chain-of-responsibility style pipeline

## Reduction strategies
1. Modularise `prompt_to_spec` into composable services
2. Strategy objects for quantifier/temporality
3. Config-driven predicate mapping (YAML/JSON)
4. Lightweight NLI (ONNX/lexical) with caching
5. Functional composition and early returns
6. Documentation at each boundary (docstrings + diagrams)
7. TDD: unit, property, integration tests

## Approximate metrics
Manual review suggests `prompt_to_spec` > 60 decision points originally; refactoring into ~6 services with ≤10 branches each keeps complexity single-digit per unit. Sanitiser complexity similarly falls when split into strategies.

## References
- `llm_endpoints.py` (recent commits)
- Services: `backend/unified/services/`
