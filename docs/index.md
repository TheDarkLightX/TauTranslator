# Tau Translator

Production-grade translation between English, Tau Controlled English (TCE), and Tau Language — combining deterministic parsing with LLM-assisted workflows.

## Get Started
- Read the full whitepaper: [WHITEPAPER.md](WHITEPAPER.md)
- Explore architecture: [Architecture → Translation Pipeline](architecture/translation_pipeline.md)
- API overview: [Reference → API](reference/index.md)

## What’s in the PoC
- Prompt→Spec (Assist-only and Generate modes)
- Parser-gated validation with repair loop (in progress)
- Knowledge packs for safe RAG (summaries, examples, embeddings)

## Roadmap (next steps)
- Constrained decoding toggle and provider matrix
- Round-trip stability suite and provenance UI
- Public demo wired to `api.tautranslator.ai`
