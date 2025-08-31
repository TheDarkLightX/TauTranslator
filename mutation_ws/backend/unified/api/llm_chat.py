from __future__ import annotations

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.unified.infrastructure.llm_providers import (
    get_provider,
    LLMRequest,
)
from .simple_tce import translate_tce_to_tau_simple
from ..domain.security import redact_pii, moderate_text, TokenBucket, validate_chat_body
from ..domain.llm_orchestrator import ChatOrchestrator
import re


router = APIRouter(prefix="/llm", tags=["llm"])
_GLOBAL_BUCKET = TokenBucket(capacity=30, refill_rate_per_sec=0.5)  # ~30 ops burst, 1 op/2s sustained


class ChatMessage(BaseModel):
    role: str  # system|user|assistant
    content: str


class ChatBody(BaseModel):
    threadId: Optional[str] = None
    messages: List[ChatMessage]
    mode: str = "assist"
    provider: Optional[str] = None
    grammar_inline: Optional[Dict[str, Any]] = None
    grammar_ref: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    threadId: str
    reply: str
    tce: Optional[str] = None
    tau: Optional[str] = None
    reasons: List[str] = []
    provenance: Dict[str, Any] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatBody, request: Request) -> ChatResponse:
    # Basic rate limit per-process (coarse). In production use per-user/key storage.
    if not _GLOBAL_BUCKET.allow():
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # Provider selection
    openrouter_key = request.headers.get("X-OpenRouter-Key")
    provider = get_provider(openrouter_key, body.provider)

    # Build prompt from messages; take last user content as primary question
    # Schema validation (strict roles, sizes) with Pydantic v1/v2 compatibility
    def _dump_msg(m: Any) -> dict:
        try:
            return m.model_dump()  # Pydantic v2
        except Exception:
            try:
                return m.dict()  # Pydantic v1
            except Exception:
                return dict(m) if isinstance(m, dict) else {"role": getattr(m, "role", ""), "content": getattr(m, "content", "")}
    _messages = [_dump_msg(m) for m in body.messages]
    ok_schema, schema_reasons = validate_chat_body(_messages)
    if not ok_schema:
        raise HTTPException(status_code=400, detail={"error": "invalid_schema", "reasons": schema_reasons})

    system_texts = [m.content for m in body.messages if m.role == "system"]
    user_texts = [m.content for m in body.messages if m.role == "user"]
    assistant_texts = [m.content for m in body.messages if m.role == "assistant"]

    # Pre-moderation: reject obviously unsafe inputs
    ok, reasons = moderate_text("\n".join(user_texts[-1:]))
    if not ok:
        raise HTTPException(status_code=400, detail={"error": "moderation_failed", "reasons": reasons})

    def _extract_grammar_hints() -> str:
        hints = []
        # Default Tau tokens
        tokens = {
            "operators": ["->", "&&", "||", "!"],
            "quantifiers": ["all", "ex"],
            "literals": ["T", "F"],
            "temporal": ["always"],
        }
        if body.grammar_inline and isinstance(body.grammar_inline, dict):
            name = body.grammar_inline.get("name", "inline")
            content = str(body.grammar_inline.get("content", ""))
            # Try to detect tokens present in grammar text
            detected = set(re.findall(r"(->|&&|\|\||!|all|ex|forall|exists|always|sometimes|T|F)", content))
            if detected:
                if "forall" in detected and "all" not in detected:
                    detected.add("all")
                if "exists" in detected and "ex" not in detected:
                    detected.add("ex")
                # merge
                tokens["operators"] = [t for t in tokens["operators"] if t in detected or t in ["->","&&","||","!"]]
                tokens["quantifiers"] = [q for q in ["all","ex"] if q in detected or q in ["all","ex"]]
                if "always" in detected:
                    tokens["temporal"] = ["always"]
            excerpt = content[:600].replace("\n", " ") if content else ""
            hints.append(f"GrammarInline: {name} (excerpt): {excerpt}")
        if body.grammar_ref and isinstance(body.grammar_ref, dict):
            hints.append(f"GrammarRef: {body.grammar_ref}")
        # Render allowed tokens succinctly
        hints.append(
            "Allowed tokens: "
            + ", ".join(tokens["operators"]) + "; quantifiers: " + ", ".join(tokens["quantifiers"]) + "; literals: T,F; temporal: always"
        )
        return "\n".join(hints)

    system = (
        "You are a Tau Controlled English (TCE) assistant.\n"
        "Rules:\n"
        "- Output exactly one TCE sentence, starting with 'always (' and ending with ')'.\n"
        "- Use only these tokens: '->' (implies), '&&', '||', '!' (not), quantifiers 'all'/'ex', literals 'T'/'F', temporal 'always'.\n"
        "- Variables are single letters (x,y,z). Do not invent new operators or punctuation.\n"
        "- No explanations, no colons, no extra text. Only the TCE inside 'always (...)'.\n"
    )
    grammar_hints = _extract_grammar_hints()
    if grammar_hints:
        system = system + "\n" + grammar_hints
    if system_texts:
        system = system + "\n" + "\n".join(system_texts)

    # Delegate to orchestrator (ports/adapters)
    orch = ChatOrchestrator(provider)
    reply, tce, tau, reasons, provenance = orch.generate_tce(_messages)

    return ChatResponse(
        threadId=body.threadId or "ephemeral",
        reply=reply,
        tce=tce,
        tau=tau,
        reasons=reasons,
        provenance={
            "mode": body.mode,
            "provider": getattr(provider, "__class__", type(provider)).__name__,
            "model": getattr(provider, "model", None),
            # Avoid logging raw prompts; store redacted
            **provenance,
        },
    )


