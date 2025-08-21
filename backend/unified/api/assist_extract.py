from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import anyio


router = APIRouter(prefix="/assist", tags=["assist"]) 


class ExtractSchema(BaseModel):
    actors: List[str] = Field(default_factory=list)
    events: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)
    postconditions: List[str] = Field(default_factory=list)
    temporal: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


class AssistExtractRequest(BaseModel):
    text: str = Field(min_length=3, max_length=20000)
    provider: str = Field(default=os.getenv("TAU_ASSIST_PROVIDER", "ollama"))
    model_id: str = Field(default=os.getenv("TAU_ASSIST_MODEL_ID", "gemma2:2b"))
    model_url: Optional[str] = Field(default=os.getenv("TAU_ASSIST_MODEL_URL", "http://127.0.0.1:11434"))
    extraction_passes: int = Field(default=1, ge=1, le=5)
    max_workers: int = Field(default=1, ge=1, le=8)
    timeout_s: float = Field(default=18.0, ge=1.0, le=60.0)


class AssistExtractResponse(BaseModel):
    ok: bool
    schema: ExtractSchema
    provenance: Dict[str, Any]
    errors: List[str] = Field(default_factory=list)


def _build_prompt() -> str:
    return (
        "Extract from the text: actors (entities that act), events (actions), "
        "preconditions (must hold before), postconditions (effects/results), "
        "temporal cues (ordering, timing), and constraints (safety, invariants). "
        "Be concise; avoid hallucinating unseen items."
    )


def _examples() -> List[Dict[str, Any]]:
    return [
        {
            "text": "When a user submits a valid login form, the system must create a session and redirect within 2 seconds.",
            "extractions": {
                "actors": ["user", "system"],
                "events": ["submits login form", "create session", "redirect"],
                "preconditions": ["login form is valid"],
                "postconditions": ["session exists", "redirect occurred"],
                "temporal": ["within 2 seconds"],
                "constraints": []
            },
        }
    ]


def _is_langextract_available() -> bool:
    try:
        import langextract  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def _run_langextract(req: AssistExtractRequest) -> ExtractSchema:
    import langextract as lx  # type: ignore

    prompt = _build_prompt()
    examples = _examples()

    kwargs: Dict[str, Any] = {
        "text_or_documents": req.text,
        "prompt_description": prompt,
        "examples": examples,
        "model_id": req.model_id,
        "extraction_passes": req.extraction_passes,
        "max_workers": req.max_workers,
        # Keep schema constraints off; we post-process into our schema
        "fence_output": False,
        "use_schema_constraints": False,
    }
    if req.provider.lower() == "ollama":
        if req.model_url:
            kwargs["model_url"] = req.model_url

    result: Dict[str, Any] = lx.extract(**kwargs)  # type: ignore

    # Normalize into our schema
    def _norm_list(x: Any) -> List[str]:
        if isinstance(x, list):
            return [str(i) for i in x if str(i).strip()]
        if isinstance(x, str):
            s = x.strip()
            return [s] if s else []
        return []

    extractions = result if isinstance(result, dict) else {}
    return ExtractSchema(
        actors=_norm_list(extractions.get("actors")),
        events=_norm_list(extractions.get("events")),
        preconditions=_norm_list(extractions.get("preconditions")),
        postconditions=_norm_list(extractions.get("postconditions")),
        temporal=_norm_list(extractions.get("temporal")),
        constraints=_norm_list(extractions.get("constraints")),
    )


@router.post("/extract", response_model=AssistExtractResponse)
async def assist_extract(req: AssistExtractRequest) -> AssistExtractResponse:
    """LLM-assisted extractor for requirements→TCE scaffolds.

    Safety:
    - Optional dependency; if unavailable, returns a clear error.
    - Local-first (Ollama). No API keys required by default.
    - Timeouts enforced; returns partial errors on failure.
    """
    if not _is_langextract_available():
        return AssistExtractResponse(
            ok=False,
            schema=ExtractSchema(),
            provenance={"provider": req.provider, "model_id": req.model_id, "unavailable": "langextract"},
            errors=["langextract not installed on server"],
        )

    start = time.time()
    errors: List[str] = []
    try:
        schema: ExtractSchema = await anyio.fail_after(req.timeout_s)(
            anyio.to_thread.run_sync, _run_langextract, req
        )
        ok = any([schema.actors, schema.events, schema.preconditions, schema.postconditions, schema.temporal, schema.constraints])
        return AssistExtractResponse(
            ok=bool(ok),
            schema=schema,
            provenance={
                "provider": req.provider,
                "model_id": req.model_id,
                "duration_ms": int((time.time() - start) * 1000),
            },
            errors=errors,
        )
    except TimeoutError:
        errors.append("extraction timed out")
    except Exception as e:  # pragma: no cover - defensive
        errors.append(str(e))
    return AssistExtractResponse(
        ok=False,
        schema=ExtractSchema(),
        provenance={
            "provider": req.provider,
            "model_id": req.model_id,
            "duration_ms": int((time.time() - start) * 1000),
        },
        errors=errors,
    )


