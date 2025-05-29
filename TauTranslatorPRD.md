Product Requirements Document (PRD): English to Tau Language Translator
Version: 0.6 (Ambitious MVP - Dual CNL/FNL & Full Coverage Mandate)
Date: 2025-05-23
Author: FIRE LIFE 1-Product Manager

1. Introduction
This document outlines the requirements for the English to Tau Language Translator, an Intelligent Specification Assistant. This tool will enable users to specify, review, and verify formal requirements using either a Controlled Natural Language (CNL) or a Flexible Natural Language (FNL). Both input modes will translate English into Tau specifications, ensuring 100% coverage of the Tau Language as defined by its official grammar, and paraphrase those specifications back into English. This dual-input strategy provides both a reliable, structured path and an intuitive, flexible path to making the entire Tau Language accessible.

2. Problem Statement
Users need to leverage Tau's full power without a steep learning curve. They require an assistant that understands their intent—whether expressed precisely (CNL) or more naturally (FNL)—and reliably translates it into any valid Tau construct. The ability to verify these constructs through English paraphrasing remains critical. This dual-input approach caters to different user preferences and learning stages while guaranteeing complete language coverage.

3. Goals and Objectives
3.1 Overall Goals
Revolutionize Accessibility: Provide multiple, English-based paths (CNL & FNL) to the entire Tau Language.
Ensure Deep Accuracy: Build confidence through bi-directional translation covering all Tau features via both CNL and FNL.
Maximize Expressiveness: Guarantee users can leverage every Tau construct via at least one documented method (CNL), aiming for FNL as well.
3.2 MVP Objectives
Dual NLU & Full Tau Mapping:
Implement a CNL parser ensuring 100% coverage of the Tau grammar with documented, specific English patterns.
Implement an FNL parser also aiming for 100% coverage, handling variations and flexibility, potentially using CNL as its 'strict' core.
Bi-Directional Translation (Full Coverage): Ensure the engine can process and generate all valid Tau constructs, originating from either CNL or FNL, and paraphrase them back to English.
Intuitive Feedback Loop: Support the iterative cycle, clearly indicating how input (CNL or FNL) was interpreted.
Deliver User Guidance: Provide comprehensive documentation for both CNL (as a reference) and FNL (as a guide).
4. Target Audience
The entire Tau Net community, offering both structured (CNL) and flexible (FNL) entry points.
5. Scope
5.1 MVP Scope (In Scope)
Controlled Natural Language (CNL) Input: A defined, documented set of English patterns mapping 1-to-1 (or near 1-to-1) with every Tau construct.
Flexible Natural Language (FNL) Input: A more lenient parser understanding variations, aiming for full Tau coverage, potentially with clarification prompts.
100% Tau Language Generation & Paraphrasing: The system must be able to generate and paraphrase every construct from the official grammar, originating from at least CNL input, and ideally FNL.
Input Mode Handling: The system must either intelligently discern between CNL/FNL or allow the user to select/influence the mode/strictness.
FNL/CNL-to-Tau Mapping: The FNL design must cover Tau; the CNL design must cover Tau.
Interactive UI: As defined in V0.4/V0.5.
Tau Syntax Validation.
Comprehensive User Guidance (CNL Reference & FNL Guide).
5.2 Future Scope (Out of Scope for MVP)
Any NLU beyond FNL.
Features beyond translation/paraphrasing/validation.
6. High-Level Features (MVP)
Dual-Mode Input:
Text area.
Access to documentation for both CNL & FNL.
(Potential Feature): A 'strictness' toggle or feedback indicating FNL confidence vs. CNL match.
Ambiguity prompts for FNL.
Bi-Directional, Full-Coverage Translation Engine: Handles both CNL (deterministically) and FNL (heuristically/AI).
Integrated Output/Review Display.
Full Tau Validation & Feedback.
Input Feedback & Suggestions (Aware of CNL/FNL).
Iterative Controls & History.
Documentation & Contextual Help.
7. User Interaction Flow (MVP)
Consult & Input: User (optionally consults docs) enters English (aiming for FNL or strictly adhering to CNL).
Translate: System processes, potentially using FNL first and indicating if it fell back to a stricter CNL interpretation or needs clarification.
Output & Paraphrase: System displays Tau, English paraphrase, and maybe how it interpreted the input (FNL/CNL match).
Review: User reviews paraphrase and Tau.
Verify/Refine: User refines input (perhaps making it stricter/CNL if FNL wasn't understood) and repeats.
8. Risks and Challenges (Adjusted)
NLU/AI Complexity (Very High): FNL and Tau-to-English remain major AI challenges.
Bi-Directional Consistency (Very High): Still very hard.
CNL/FNL Design (Extreme): Designing both a comprehensive CNL and an FNL, and ensuring they coexist or layer well, is even more complex.
Full Tau Coverage Complexity (Very High): Still a massive task to map everything.
User Experience (High): Managing user expectations and providing clarity when switching between or interpreting FNL/CNL adds UX complexity.
Scope & Resources (Extreme): This remains an exceptionally large R&D project. The dual-input adds design/dev load but provides a 'safer' path to 100% coverage via CNL.

