Epic 1: Foundation - Tau Grammar & CNL Engine
ID: EPIC-1
Title: Foundation - Tau Grammar & CNL Engine
Goal: To establish the core infrastructure capable of understanding the full Tau Language grammar and translating a defined Controlled Natural Language (CNL) into 100% compliant Tau Language specifications. This forms the reliable bedrock for all other features.
Scope:
Implement a robust parser for the official Tau Language grammar (tau.tgf, bitvector.tgf, etc.).
Design the complete Controlled Natural Language (CNL), ensuring every Tau construct has a defined, documented CNL pattern.
Build the translation engine to convert CNL input into syntactically valid Tau code.
Implement a Tau syntax validator based on the parser to check generated code.
Focus only on the CNL-to-Tau path for this epic. FNL and Tau-to-English are out of scope here.
Potential User Story Areas:
As a user, I can define [Specific Tau Construct] using its documented CNL pattern so that it translates to the correct Tau code. (Repeat for all Tau constructs: Assignments, Booleans, Temporal, Quantifiers, Bitvectors, Definitions, etc.)
As a developer, I can validate a string of Tau code against the official grammar so that I know if it's syntactically correct.
As a user, I receive a clear error if my input does not match a defined CNL pattern.
Dependencies: Tau Language Grammar files.
Risks: Underestimating the complexity of mapping all Tau features to CNL; ensuring the parser is 100% compliant.
Epic 2: Verification - Tau-to-English Paraphrasing (CNL Focus)
ID: EPIC-2
Title: Verification - Tau-to-English Paraphrasing (CNL Focus)
Goal: To enable users to verify generated Tau code by providing a clear, understandable English paraphrase based on the Controlled Natural Language definitions.
Scope:
Build an engine that takes any valid Tau Language specification as input.
Parse the Tau code using the grammar established in EPIC-1.
Generate an English-language description based on the pre-defined CNL patterns. This ensures the paraphrase is consistent with the 'official' way of expressing things in CNL.
Handle all Tau constructs.
Focus is on Tau -> CNL English; FNL is out of scope.
Potential User Story Areas:
As a user, I can input a [Specific Tau Construct] and see its corresponding CNL English paraphrase so that I can verify its meaning. (Repeat for all Tau constructs).
As a user, I can see a full Tau specification paraphrased into a sequence of CNL English sentences.
Dependencies: EPIC-1 (Tau Parser, CNL Definition).
Risks: Ensuring the paraphrase is accurate and truly reflects the Tau semantics, especially for complex constructs, while sticking to CNL; handling nested/complex structures in a readable way.
Epic 3: Intelligence - FNL Engine
ID: EPIC-3
Title: Intelligence - FNL Engine
Goal: To provide users with a more intuitive and flexible way to input specifications by understanding variations in natural language (FNL) and mapping them to Tau constructs.
Scope:
Develop or integrate a Natural Language Understanding (NLU) component.
Define the range of flexibility (synonyms, sentence structures) the FNL engine will attempt to handle.
Build the logic to map FNL inputs to the canonical Tau structures (potentially by first mapping FNL to CNL or directly to Tau).
Implement ambiguity detection and (potentially) clarification mechanisms.
Aim for full Tau coverage via FNL, acknowledging this is a significant AI challenge.
Potential User Story Areas:
As a user, I can use [Synonym/Alternative Phrasing] for a CNL pattern and have it translate correctly.
As a user, if I provide an ambiguous FNL input, the system asks me to clarify my intent.
As a user, I can express [Complex Tau Construct] using a more conversational FNL style.
Dependencies: EPIC-1 (Core Tau understanding).
Risks: NLU complexity (very high); achieving high accuracy/coverage; managing ambiguity; performance. This is the primary R&D epic.
Epic 4: Interaction - UI/UX & Workflow
ID: EPIC-4
Title: Interaction - UI/UX & Workflow
Goal: To create a seamless and intuitive user interface that supports the complete, iterative Input -> Output -> Paraphrase -> Review -> Verify -> Refine workflow, handling both CNL and FNL inputs effectively.
Scope:
Design and build the primary user interface (likely web-based).
Implement input areas, output displays (showing English, Tau, Paraphrase), and translation triggers.
Integrate validation feedback and error messaging.
Handle CNL/FNL mode switching or indication.
Implement ambiguity clarification prompts (if part of EPIC-3).
Ensure easy access to documentation/help.
Potential User Story Areas:
As a user, I can type my English spec, press 'Translate', and see the Tau and English paraphrase side-by-side.
As a user, I can easily edit my English input and re-translate.
As a user, I can see clear error messages and validation feedback integrated into the UI.
As a user, I understand if the system interpreted my input as strict CNL or flexible FNL.
As a user, I can easily access help/documentation from the UI.
Dependencies: EPIC-1, EPIC-2, EPIC-3 (to provide the backend functionality).
Risks: Designing a UI that can handle this complexity without being cluttered; making the FNL clarification process intuitive.
Epic 5: Enablement - Documentation & Guidance
ID: EPIC-5
Title: Enablement - Documentation & Guidance
Goal: To empower users to effectively use the translator by providing clear, comprehensive, and easily accessible documentation for both CNL and FNL, covering all Tau features.
Scope:
Create a detailed CNL Reference Manual: This must list every Tau construct and its precise CNL English pattern(s). It's the 'source of truth'.
Create an FNL User Guide: This will teach users how to interact using FNL, provide examples, explain common patterns, and describe how ambiguity is handled.
Develop contextual help within the UI (linking to docs).
Create tutorials or example specifications.
Potential User Story Areas:
As a new user, I can read a tutorial to understand the basic workflow.
As a user, I can look up any Tau construct in the CNL manual to find its exact English pattern.
As a user, I can read the FNL guide to learn how to write more naturally.
As a user, I can click a 'Help' icon next to a feature to get relevant documentation.
Dependencies: EPIC-1 (CNL definition), EPIC-3 (FNL capabilities), EPIC-4 (UI for contextual help).
Risks: Ensuring documentation is 100% accurate and covers all features; keeping docs updated as the system evolves; making it understandable for non-experts.
