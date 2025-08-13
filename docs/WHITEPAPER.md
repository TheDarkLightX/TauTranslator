## Tau Translator Whitepaper (Public PoC Blueprint)

### Abstract
Tau Translator is a production-grade system for bidirectional translation among plain English, Tau Controlled English (TCE), and Tau Language. It combines deterministic parsing and validation with LLM-assisted generation to deliver a secure, license-compliant, and verifiable pipeline. The system adopts Railway Oriented Programming (ROP) for robust error handling, Test-Driven Development (TDD) for quality, and Clean Architecture for maintainability. This whitepaper doubles as a GitHub blueprint for a public proof-of-concept (PoC) without source disclosure, guiding API contracts, UX, evaluation metrics, and a compliance-first operation model.

### Motivation and Vision
- Reduce ambiguity in natural language specifications by translating to verifiable formal representations.
- Enable engineers, product managers, and domain experts to iterate specs safely using TCE as an intermediate layer.
- Combine deterministic parsing with LLM assistance to accelerate specification workflows while maintaining correctness guarantees.

### Scope
- English ↔ TCE ↔ Tau (round-trip where semantics permit).
- Canonical parser for TCE is Lark; optimized Pratt parser is available for fast iteration. A parser adapter abstracts selection and fallback.
- LLM features provide two user-selectable modes:
  - Assist-only: model proposes suggestions/snippets; user curates.
  - Generate Spec (Prompt→Spec): model proposes full TCE; deterministic parser validates, triggers repair loop if invalid.
- Public PoC: shows functionality and endpoints without revealing source code or licensed content.

### Non-Goals
- Encoding or embedding raw licensed Tau grammar in the product or prompts.
- Guaranteeing full natural language coverage; we prioritize controlled subsets and explain limitations clearly.

### Core Principles
- Railway Oriented Programming (ROP): every step returns Result(success | failure), enabling composable, declarative control flow and predictable error handling.
- TDD and Clean Code: tests first, minimal implementations, small modules, strong boundaries, and explicit contracts.
- License Compliance: strict non-embedding of raw grammar; load grammars at runtime where permitted, derive license-safe knowledge packs.
- Intentional Disclosure: clear separation between internal logic and public APIs; no secret leakage in responses or logs.

### Architecture Overview
- Presentation layer: PWA + Desktop (PyQt) with an identical interaction model.
- API layer: FastAPI endpoints for Prompt→Spec, Spec→Prompt, validations, and translation.
- Domain layer: translation pipelines, ILR (Intermediate Logic Representation), validators, policy.
- Parsing: canonical Lark grammar for TCE, optimized Pratt parser for expressions; unified through a parser adapter.
- LLM layer: provider abstraction (local + external), constrained decoding, RAG via knowledge packs, validation/repair loop gated by parsers.
- Storage: license-safe knowledge packs (summaries, examples, embeddings, prompts, evals), no raw grammar content stored.
- Observability: structured logs, metrics, traces, content policy checks.

### Parsers and Canonical Path
- Canonical TCE parser: Lark.
- Optimized Pratt parser: O(n) precedence parser for efficient expression parsing and robustness during development.
- Parser adapter: chooses canonical Lark by default; falls back to Pratt on initialization or validation failure (configurable).
- Complexity:
  - Pratt: O(n) tokens.
  - Lark: O(n) to O(n log n) depending on grammar; practical performance is sufficient for PoC and production.

### Intermediate Logic Representation (ILR)
- Purpose: decouple surface syntax (TCE) from target Tau output; supports round-trip reasoning and LLM validation prompts.
- Properties:
  - Node types: entities, relations, quantifiers, connectives, predicates, constants, arithmetic operators.
  - Deterministic transforms: TCE→ILR→Tau, Tau→ILR→TCE where feasible.
  - Validations: type checks, scoping, binding, quantifier placement, arity and signature checks.

### Translation Pipelines
- English→TCE:
  - LLM proposes controlled language candidates (Assist or Generate).
  - Parser validates candidates; if invalid, run a repair loop with explicit diff and error explanations.
- TCE→Tau:
  - Deterministic transforms via ILR; parser re-check ensures invariants.
- Tau→TCE:
  - Deterministic or heuristic transforms based on grammar mapping and ILR graphs.
- Round-trip checks:
  - Optional: TCE→Tau→TCE identity check on a constrained subset; differences surfaced as suggestions with rationales.

### LLM Integration
- Providers:
  - External: OpenAI, OpenRouter, Anthropic, and others.
  - Local: llama.cpp, text-generation-webui, vLLM.
- Modes:
  - Assist-only: suggestions are annotated and never auto-accepted.
  - Generate Spec: full TCE proposed; must pass parser validation or invoke repair loop.
- Constrained decoding:
  - Techniques: JSON/regex schemas and grammar-constrained decoding for controlled segments.
  - Policy: constraints must align with controlled syntax; avoid embedding raw licensed grammar.
- RAG with Knowledge Packs:
  - License-safe packs: concept summaries, examples, embeddings, evaluation snippets.
  - Retrieval: top-k semantic search with safety filters; notes on provenance and licensing.
- Validation/Repair loop:
  - Parse TCE; on failure, provide structured errors to the model.
  - Iteratively patch minimal changes (e.g., missing punctuation, connective rule enforcement).
  - Hard stop after N attempts; return actionable errors to the user.

### Grammar Knowledge Packs (License-Safe)
- Content types: summaries of syntax and semantics per concept, examples curated for coverage, embeddings for retrieval, evaluation prompts, and red-teaming hints.
- Build process: runtime access (if permitted) to official grammar or community versions; immediately derive summaries without storing verbatim grammar content. Store only derivative artifacts and provenance metadata.
- Safety checks: no verbatim grammar fragments beyond minimal fair-use references; automated scanners for leakage (regexes + embedding similarity).
- RAG pipeline: query → retrieve top-k items → prompt augmentation → constrained decoding → parse/validate → accept/repair.

### Railway Oriented Programming (ROP)
- Result type: Success carries typed payloads; Failure carries error code, message, and details.
- Composition: chain transformations with map/bind semantics; guard clauses for invariants.
- Error taxonomy: ParserError, TransformError, PolicyError, ProviderError, TransientError (retryable), ValidationError (repairable).

### Security and Privacy
- Threat model: prompt injection; output poisoning that bypasses parser; SSRF via provider webhooks; PII leakage; license leakage.
- Controls: strict parser validation on all LLM outputs; redaction/normalization; output filtering; per-provider API quotas, timeouts, circuit breakers; secrets via environment variables; CORS/CSRF protections; CSP headers; audit logs for moderation events; deterministic replay for dispute resolution.
- License compliance: no raw grammar embedded in prompts or storage; only derived, safe summaries in knowledge packs; runtime-only access to official grammar, if permitted, with ephemeral handling.

### UX: PWA + Desktop
- Core interactions: two-pane editor (plain English/TCE ↔ Tau/ILR preview); mode toggles (Assist vs Generate, provider selection, constrained decoding); validation lane (live errors, suggested repairs); diff and trace view for round-trip; provenance notes for RAG items.
- Accessibility and polish: keyboard-first flows, semantic headings, high-contrast themes, examples and tooltips, offline-ready PWA, low-latency local provider option.

### Public PoC: API Contracts (No Source Disclosure)
- Prompt→Spec
  - POST `/llm/prompt-to-spec`
  - Request: `{ "prompt": string, "mode": "assist"|"generate", "provider"?: string }`
  - Response: `{ "success": boolean, "tce": string|null, "tau": string|null, "reasons": string[] }`
- Spec→Prompt
  - POST `/llm/spec-to-prompt`
  - Request: `{ "tce"?: string, "tau"?: string }`
  - Response: `{ "prompt": string, "explanations": string[] }`
- Validate TCE
  - POST `/validate/tce`
  - Request: `{ "tce": string }`
  - Response: `{ "valid": boolean, "errors": string[] }`
- Translate TCE→Tau
  - POST `/translate/tce-to-tau`
  - Request: `{ "tce": string }`
  - Response: `{ "success": boolean, "tau": string|null, "errors": string[] }`
- Retrieve RAG
  - GET `/rag/retrieve?query=...&k=...`
  - Response: `{ "items": [{ "id": string, "title": string, "snippet": string, "score": number, "provenance": { "source": string, "license": string } }] }`

All endpoints return ROP-shaped envelopes and never leak secrets or licensed content.

### Testing and Quality (TDD)
- Strategy: write tests before feature code; smallest passing implementation; EP/BVA on parser inputs and LLM outputs; decision tables for assist/generate behaviors.
- Automated tests: unit (parsers, ILR, Result, validators), contract (API schemas, negative cases), property-based (round-trip invariants on constrained subsets), mutation tests (validators effectiveness).
- Performance baselines: Pratt parse = O(n) tokens; Lark acceptance thresholds pinned by test data.
- Quality gates: coverage thresholds; regression snapshot; complexity limits per file to preserve maintainability.

### Observability
- Logs: structured JSON with redaction.
- Metrics: parse pass/fail rates, repair iterations, endpoint latency, provider error rates.
- Traces: request spans for API, parser, LLM provider calls, RAG steps.

### Deployment Blueprint (PoC)
- Hosting: containerized FastAPI over HTTPS with reverse proxy.
- Secrets: `.env` mounted in runtime only; CI masked.
- Providers: toggleable via env flags; safe defaults to local provider.
- Rate limiting and quotas per IP/API key; abuse prevention for public demo.
- Feature flags: assist-only default; generate-spec requires explicit opt-in.

### Roadmap
- M1: Green-path validation and translation with repair loop; assist mode polished.
- M2: Constrained decoding integration; provider matrix (OpenAI/OpenRouter/local).
- M3: Knowledge packs with embeddings and provenance UI; RAG eval harness.
- M4: Round-trip stability suite; UX refinements; accessibility audits.
- M5: MCP bridge for advanced AoT tooling; export/import ecosystems.

### Evaluation and Benchmarks
- Correctness: parser acceptance, ILR invariants, round-trip fidelity on a curated corpus.
- Usability: time-to-valid-spec, number of repair iterations, user satisfaction surveys.
- Safety: license leakage rate (target zero), prompt injection resilience tests.
- Cost: per-request compute and provider costs; cache hit ratios.

### AoT Integration
- CLI orchestrator: `decompose`, `solve-atom`, `compose`, `tce-validate`, `tce-to-tau` to anchor AoT steps to deterministic checks.
- Future MCP bridge: optional JSON-RPC server exposing the same primitives for IDE assistants.

### Appendix A: Representative JSON Schemas
- Result envelope: `{ "success": boolean, "data": any|null, "error": { "code": string, "message": string, "details": object|null } | null }`
- RAG item: `{ "id": string, "title": string, "snippet": string, "score": number, "provenance": { "source": string, "license": string } }`

### Appendix B: Compliance Policy Highlights
- No storage or prompts include verbatim licensed grammar content.
- Derived knowledge packs log provenance; automated leakage scans run in CI.
- Runtime downloads are ephemeral; caches store only derivative summaries.

### Appendix C: Risk Register (PoC)
- Constrained decoding gaps can allow off-grammar outputs → mitigated by deterministic parser gating + repair loop.
- Provider variability (format/latency) → mitigated by provider abstraction and per-provider adapters.
- Public demo abuse → mitigated by rate limits, safelists, and curated demo modes.


