"""
Strategy for translating Tau code to natural language.
"""

from typing import List
import asyncio

from returns.result import Result, Success, Failure

from backend.unified.core.domain_types import AppError, SourceText
from backend.unified.core.llm_client import LLMClient
from .base import TranslationEngine, TranslationResult, TranslationDirection


class TauToNaturalLanguageStrategy(TranslationEngine):
    """Translates Tau code to natural language using an LLM."""

    def __init__(self, llm_client: LLMClient):
        super().__init__(name="tau_to_nl_strategy", description="Translates Tau to NL.")
        self._llm_client = llm_client

    def get_supported_directions(self) -> List[TranslationDirection]:
        return [TranslationDirection.TAU_TO_NL]

    def can_translate(self, text: SourceText, direction: TranslationDirection) -> bool:
        return direction == TranslationDirection.TAU_TO_NL

    def translate(self, text: SourceText, direction: TranslationDirection, **kwargs) -> Result[TranslationResult, AppError]:
        """Synchronous wrapper for the async translate method."""
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # 'get_running_loop' fails if no loop is running
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self.translate_async(text, direction, **kwargs))

    async def translate_async(self, text: SourceText, direction: TranslationDirection, **kwargs) -> Result[TranslationResult, AppError]:
        if not self.can_translate(text, direction):
            return Failure(AppError(error_code="UNSUPPORTED_TRANSLATION", message="Unsupported translation direction"))

        prompt = self._create_prompt(text)
        llm_result = await self._llm_client.query_async(prompt)

        if isinstance(llm_result, Success):
            translated_text = llm_result.unwrap()
            return Success(self._create_result(
                success=True,
                translated_text=translated_text,
                original_text=text,
                direction=direction,
                confidence=0.9  # Confidence is high as it's a direct LLM translation
            ))
        else:
            return Failure(AppError(error_code="LLM_ERROR", message="LLM query failed"))

    def _create_prompt(self, tau_code: str) -> str:
        return f"""You are an expert in formal logic and the Tau programming language.
        Please translate the following Tau code into clear, natural English.

        Tau Code:
        ```tau
        {tau_code}
        ```

        English Translation:"""
