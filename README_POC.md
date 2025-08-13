## Tau Translator — Public PoC

This page presents a public proof-of-concept (PoC) for Tau Translator. The PoC demonstrates deterministic parsing/validation and LLM-assisted workflows without disclosing source code or licensed grammar content.

### What You Can Do
- Prompt→Spec (English→TCE) in Assist or Generate modes
- Validate TCE and Translate TCE→Tau
- Retrieve license-safe knowledge pack snippets used to inform LLMs

### Endpoints
- POST `/llm/prompt-to-spec` — `{ "prompt": string, "mode": "assist"|"generate", "provider"?: string }`
- POST `/llm/spec-to-prompt` — `{ "tce"?: string, "tau"?: string }`
- POST `/validate/tce` — `{ "tce": string }`
- POST `/translate/tce-to-tau` — `{ "tce": string }`
- GET `/rag/retrieve?query=...&k=...`

All responses use ROP-style envelopes and never include secrets or licensed content.

### Modes and Safety
- Assist-only defaults ON for public demo; Generate Spec requires explicit opt-in.
- All LLM outputs are gated by deterministic parsers; invalid outputs trigger a repair loop.
- Knowledge packs contain derivative summaries and examples; they never include raw licensed grammar.

### Demo Ideas
- Try: `"x equals 5"` → Prompt→Spec (Assist), then Validate, and Translate to Tau.
- Try: `"forall x : x equals 5"` and compare round-trip behavior.

### Roadmap
- Constrained decoding integration and provider matrix (OpenAI/OpenRouter/local)
- Embedding-powered retrieval with provenance UI
- Round-trip stability suite and accessibility polish

For the full blueprint, see `docs/WHITEPAPER.md`.


