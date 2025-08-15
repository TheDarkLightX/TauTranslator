from __future__ import annotations

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.unified.infrastructure.llm_providers import (
    get_provider,
    LLMRequest,
)
from .simple_tce import translate_tce_to_tau_simple


router = APIRouter(prefix="/llm", tags=["llm"])


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
    # Provider selection
    openrouter_key = request.headers.get("X-OpenRouter-Key")
    provider = get_provider(openrouter_key, body.provider)

    # Build prompt from messages; take last user content as primary question
    system_texts = [m.content for m in body.messages if m.role == "system"]
    user_texts = [m.content for m in body.messages if m.role == "user"]
    assistant_texts = [m.content for m in body.messages if m.role == "assistant"]

    system = (
        "You are a helpful Tau Controlled English (TCE) assistant."
        " Produce at most one TCE sentence starting with 'always (' and ending with ')'."
        " Use Tau quantifiers 'all'/'ex', '->' for implies, '!' for not."
        " Avoid colons and invalid tokens."
    )
    if system_texts:
        system = system + "\n" + "\n".join(system_texts)

    prior = "\n".join(f"Assistant: {t}" for t in assistant_texts[-3:])
    question = user_texts[-1] if user_texts else ""

    steering = []
    if body.grammar_ref:
        steering.append(f"GrammarRef: {body.grammar_ref}")
    if body.grammar_inline:
        steering.append(f"GrammarInline: {body.grammar_inline.get('name','inline')}")

    prompt = (
        ("\n".join(steering) + "\n" if steering else "")
        + (f"Context:\n{prior}\n" if prior else "")
        + f"User: {question}\nTCE:"
    )

    gen = provider.generate(LLMRequest(prompt=prompt, system=system, temperature=0.2, max_tokens=160))
    if isinstance(gen, tuple) and getattr(gen, "is_failure", False):  # defensive for older Result types
        raise HTTPException(status_code=500, detail=str(gen))

    reply = gen.unwrap().text if hasattr(gen, "unwrap") else gen.value.text  # type: ignore

    # Sanitize to single-line TCE
    tce = reply.strip()
    # Basic normalization
    if not tce.lower().startswith("always ("):
        tce = f"always ({tce})" if not tce.endswith(")") else f"always ({tce})"
    tce = tce.replace(":", " ")

    tau = None
    reasons: List[str] = []
    try:
        ok, tau_simple, errs = translate_tce_to_tau_simple(tce)
        if ok and tau_simple:
            tau = tau_simple
        else:
            reasons.extend(errs)
    except Exception as e:
        reasons.append(str(e))

    return ChatResponse(
        threadId=body.threadId or "ephemeral",
        reply=reply,
        tce=tce,
        tau=tau,
        reasons=reasons,
        provenance={
            "mode": body.mode,
            "provider": body.provider or ("openrouter" if openrouter_key else "echo"),
            "steering": steering,
        },
    )


