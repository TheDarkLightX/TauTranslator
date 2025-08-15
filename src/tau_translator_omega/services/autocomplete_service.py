"""
Orchestrates the autocomplete workflow using a railway-oriented pipeline.

This service acts as the high-level entry point for autocomplete requests. It
composes functions from the `infrastructure` and `core` layers into a single,
robust data processing pipeline using the `returns` library.

The public method `get_suggestions_for_request_async` demonstrates the
Intentional Disclosure Principle: its structure clearly reveals the sequence of
operations (parsing, NLP processing, suggestion generation) without exposing the
low-level implementation details.

Copyright: DarkLightX / Dana Edwards
"""

from returns.pointfree import bind
from returns.pipeline import flow

from tau_translator_omega.core_engine.autocomplete.domain import (
    AutocompleteRequest,
    AutocompleteResult,
)
from tau_translator_omega.core_engine.autocomplete.pipelines import (
    generate_suggestions_from_context,
)
from tau_translator_omega.infrastructure.nlp_adapter import (
    extract_linguistic_features,
    get_nlp_model,
)
from tau_translator_omega.infrastructure.parser_adapter import parse_text_to_ast


class NLPAutocompleteService:
    """A high-level service for providing NLP-powered autocomplete suggestions."""

    async def get_suggestions_for_request_async(
        self, request: AutocompleteRequest
    ) -> AutocompleteResult:
        """Processes an autocomplete request through a safe, declarative pipeline.

        This method is the primary entry point. It follows a railway-oriented
        approach where each step in the pipeline must succeed for the next to
        be executed. A failure at any point short-circuits the pipeline and
        returns a `Failure` container with a specific error.

        Args:
            request: The autocomplete request containing the text and cursor info.

        Returns:
            An `AutocompleteResult` container which is either a `Success` with a
            list of suggestions or a `Failure` with an `AutocompleteError`.
        """
        # This is the railway pipeline. It reads from top to bottom.
        # 1. Start by getting the NLP model.
        # 2. `bind` to the next step: if getting the model succeeded, parse the text.
        #    The `map` inside creates a tuple of (ast, nlp_model) for the next step.
        # 3. `bind` again: if parsing succeeded, extract linguistic features.
        #    The `map` inside creates a tuple of (ast, nlp_doc) for the core logic.
        # 4. `bind` one last time to the pure suggestion generation logic.
        return flow(
            get_nlp_model(),
            bind(lambda nlp: parse_text_to_ast(request.text).map(lambda ast: (ast, nlp))),
            bind(
                lambda context: extract_linguistic_features(
                    request.text, context[1]
                ).map(lambda doc: (context[0], doc))
            ),
            bind(generate_suggestions_from_context),
        )
