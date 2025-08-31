from __future__ import annotations

from typing import List, Dict, Any, Tuple
import re

from ..infrastructure.llm_providers import LLMRequest, LLMProvider
from ..api.simple_tce import translate_tce_to_tau_simple
from .security import redact_pii


class ChatOrchestrator:
    """Encapsulates LLM prompt construction and response sanitization for chat.

    Ports/Adapters style: this class is the domain service (port) that consumes
    a provider (adapter). It applies consistent prompting and post-processing.
    """

    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    @staticmethod
    def _extract_grammar_hints(grammar_inline: Dict[str, Any] | None, grammar_ref: Dict[str, Any] | None) -> str:
        hints: List[str] = []
        tokens = {
            "operators": ["->", "&&", "||", "!"],
            "quantifiers": ["all", "ex"],
            "literals": ["T", "F"],
            "temporal": ["always"],
        }
        if grammar_inline and isinstance(grammar_inline, dict):
            name = grammar_inline.get("name", "inline")
            content = str(grammar_inline.get("content", ""))
            detected = set(re.findall(r"(->|&&|\|\||!|all|ex|forall|exists|always|T|F)", content))
            if detected:
                if "forall" in detected and "all" not in detected:
                    detected.add("all")
                if "exists" in detected and "ex" not in detected:
                    detected.add("ex")
            excerpt = content[:600].replace("\n", " ") if content else ""
            hints.append(f"GrammarInline: {name} (excerpt): {excerpt}")
        if grammar_ref and isinstance(grammar_ref, dict):
            hints.append(f"GrammarRef: {grammar_ref}")
        hints.append(
            "Allowed tokens: "
            + ", ".join(tokens["operators"]) + "; quantifiers: " + ", ".join(tokens["quantifiers"]) + "; literals: T,F; temporal: always"
        )
        return "\n".join(hints)

    @staticmethod
    def _build_system(base_system: str, extra: str | None, grammar_inline: Dict[str, Any] | None, grammar_ref: Dict[str, Any] | None) -> str:
        out = base_system
        hints = ChatOrchestrator._extract_grammar_hints(grammar_inline, grammar_ref)
        if hints:
            out = out + "\n" + hints
        if extra:
            out = out + "\n" + extra
        return out

    @staticmethod
    def _sanitize_tce(reply_text: str, user_question: str) -> str:
        text = (reply_text or "").strip()
        # Remove known labels the model may echo
        text = re.sub(r"\b(Context:|User:|Assistant:|TCE:)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s+", " ", text).strip()
        # Extract the first balanced 'always ( ... )'
        lower = text.lower()
        start = lower.find("always (")
        if start != -1:
            depth = 0
            end = None
            for i in range(start, len(text)):
                ch = text[i]
                if ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end is not None and end > start:
                return text[start : end + 1]
            # Fallback: return from start to end if no full balance found
            return text[start:]
        # Fall back to wrapping the user question (label-free)
        uq = re.sub(r"\b(Context:|User:|Assistant:|TCE:)\b", "", user_question or "", flags=re.IGNORECASE)
        inner = uq.replace(':', ' ').strip()
        return f"always ({inner})"

    def generate_tce(self, messages: List[Dict[str, str]], temperature: float = 0.2, max_tokens: int = 160, *, grammar_inline: Dict[str, Any] | None = None, grammar_ref: Dict[str, Any] | None = None) -> Tuple[str, str, str | None, List[str], Dict[str, Any]]:
        system_texts = [m["content"] for m in messages if m.get("role") == "system"]
        user_texts = [m["content"] for m in messages if m.get("role") == "user"]
        assistant_texts = [m["content"] for m in messages if m.get("role") == "assistant"]
        # Base system rules
        base_system = (
            "You are a Tau Controlled English (TCE) assistant.\n"
            "Rules:\n"
            "- Output exactly one TCE sentence, starting with 'always (' and ending with ')'.\n"
            "- Use only these tokens: '->' (implies), '&&', '||', '!' (not), quantifiers 'all'/'ex', literals 'T'/'F', temporal 'always'.\n"
            "- Variables are single letters (x,y,z). Do not invent new operators or punctuation.\n"
            "- No explanations, no colons, no extra text. Only the TCE inside 'always (...)'.\n"
        )
        # Grammar steering collected externally via args (if provided)
        # Derive extra system (concatenate any system messages)
        extra_system = "\n".join(system_texts) if system_texts else None
        system = self._build_system(base_system, extra_system, grammar_inline, grammar_ref)

        prior = "\n".join(f"Assistant: {t}" for t in assistant_texts[-3:])
        question = user_texts[-1] if user_texts else ""
        prompt = ((f"Context:\n{prior}\n" if prior else "") + f"User: {question}\nTCE:")

        # Redact before sending to provider
        safe_system = redact_pii(system)
        safe_prompt = redact_pii(prompt)
        req = LLMRequest(prompt=safe_prompt, system=safe_system, temperature=temperature, max_tokens=max_tokens)
        gen = self.provider.generate(req)
        if hasattr(gen, "is_failure") and gen.is_failure():
            # Propagate failure details upstream
            return "", "", None, [str(gen)], {"system_redacted": safe_system[:200], "prompt_redacted": safe_prompt[:200]}

        reply = gen.unwrap().text  # type: ignore
        tce = self._sanitize_tce(reply, user_question=question)

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

        provenance = {
            "prompt_redacted": safe_prompt[:256],
            "system_redacted": safe_system[:256],
        }
        return reply, tce, tau, reasons, provenance


