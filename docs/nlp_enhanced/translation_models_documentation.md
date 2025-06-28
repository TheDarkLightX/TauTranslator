# Documentation: NLP Translation Data Models

**File:** `src/tau_translator_omega/core_engine/translators/nlp_enhanced/translation_models.py`

This document provides a detailed explanation of the data models used by the NLP-enhanced translation system. These models are fundamental to passing structured data through the translation pipeline, from initial semantic analysis to the final Tau specification.

---

## 1. `ConfidenceScore`

This data class provides a granular, multi-faceted score for each translation, offering deeper insight than a single float value.

-   **`overall` (`float`):** The final, aggregated confidence score for the translation.
-   **`syntax` (`float`):** Confidence in the syntactic correctness of the source text.
-   **`semantics` (`float`):** Confidence in the accuracy of the semantic interpretation (entities, predicates).
-   **`logical_structure` (`float`):** Confidence that the logical and temporal structure has been correctly identified.
-   **`mathematical` (`float`):** Confidence specifically for the interpretation of mathematical expressions or constraints.
-   **`issues` (`List[str]`):** A list of human-readable strings describing any specific issues or ambiguities that were detected during translation, which may have lowered the confidence scores.

---

## 2. `SemanticAnalysis`

This data class holds the structured output of the semantic analysis phase, breaking down the source text into its core components.

-   **`predicates` (`List[str]`):** The key actions or verbs identified in the sentence.
-   **`entities` (`List[str]`):** The key actors or nouns.
-   **`quantifiers` (`List[str]`):** Any universal or existential quantifiers (e.g., "all", "some").
-   **`logical_operators` (`List[str]`):** Logical connectives like "and", "or", "not".
-   **`temporal_expressions` (`List[str]`):** Phrases related to time or sequence (e.g., "after", "while").

---

## 3. `TranslationResult`

This is the primary data model for representing the outcome of translating a single sentence or requirement.

-   **`source_text` (`str`):** The original English text that was translated.
-   **`tau_specification` (`str`):** The generated Tau Language specification.
-   **`confidence` (`ConfidenceScore`):** A detailed breakdown of the confidence in the translation.
-   **`semantic_analysis` (`SemanticAnalysis`):** The structured semantic components extracted from the source text.
-   **`amr_graph` (`Optional[AMRGraph]`):** An optional Abstract Meaning Representation (AMR) graph, providing a deep semantic representation of the text.
-   **`translation_notes` (`Optional[List[str]]`):** Optional notes from the translator about specific choices or ambiguities.

---

## 4. `DocumentTranslationResult`

This data class aggregates the results of translating an entire document, providing a complete picture and ensuring traceability.

-   **`source_document` (`str`):** The full original source document.
-   **`tau_specification` (`str`):** The complete, concatenated Tau specification for the entire document.
-   **`individual_translations` (`List[TranslationResult]`):** A list of `TranslationResult` objects, one for each sentence or requirement translated. This allows for detailed inspection of each part of the translation.
-   **`overall_confidence` (`float`):** An aggregated confidence score for the entire document translation.
-   **`traceability_map` (`Dict[str, str]`):** A dictionary mapping snippets of the source text to the corresponding lines in the generated Tau specification, providing crucial traceability.
