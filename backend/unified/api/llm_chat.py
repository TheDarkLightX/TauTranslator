from __future__ import annotations

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.unified.infrastructure.llm_providers import (
    get_provider,
    LLMRequest,
)
from .simple_tce import translate_tce_to_tau_simple
import re


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

    prior = "\n".join(f"Assistant: {t}" for t in assistant_texts[-3:])
    question = user_texts[-1] if user_texts else ""

    prompt = (
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
            "provider": getattr(provider, "__class__", type(provider)).__name__,
            "model": getattr(provider, "model", None),
            "steering": steering,
        },
    )


