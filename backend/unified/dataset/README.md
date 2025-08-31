# Dataset Builder (Offline-First)

This module helps build NL↔TCE corpora for evaluation and optional fine‑tuning.

## Pipeline
1. Seed small, high‑quality pairs in YAML:
```yaml
- nl: If A then B
  tce: always (A -> B)
```
2. Paraphrase offline with simple rewrites (placeholder for LLM paraphrases).
3. Validate TCE deterministically via token gating and simple tce→tau translation.
4. Save JSONL for downstream training/evaluation.

## CLI (example)
You can script these functions in a notebook or add a wrapper CLI as needed.

## Notes
- Keep models offline by default; if you add LLM paraphrasing later, gate it via env flags and fail closed.
- Use round‑trip checks and/or human review for high‑stakes datasets.
