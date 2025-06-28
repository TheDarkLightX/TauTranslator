#!/usr/bin/env python3
"""
Requirements Analyzer following the Intentional Disclosure Principle.

This module analyzes natural language requirements for conversion to formal Tau specifications.
- All methods under 10 lines with single responsibility
- Domain types replace primitives for type safety
- I/O operations isolated in repositories
- Business logic separated from infrastructure

Copyright: DarkLightX / Dana Edwards
"""

from typing import ClassVar, Dict, List, Optional, Set, Any, Tuple, NewType, Protocol
from dataclasses import dataclass, field
from enum import Enum, auto
import re
from collections import defaultdict

from .requirements_models import (
    FormalConstraint,
    LogicalStructure,
    RequirementCategory,
    RequirementItem,
    RequirementType,
)

# Domain Types (Rule 3: Maximize Disclosure via Type System)
RequirementText = NewType("RequirementText", str)
SentenceText = NewType("SentenceText", str)
SectionTitle = NewType("SectionTitle", str)
SectionContent = NewType("SectionContent", str)
EntityName = NewType("EntityName", str)
PredicateName = NewType("PredicateName", str)
ConfidenceScore = NewType("ConfidenceScore", float)
LogicalFormula = NewType("LogicalFormula", str)
PatternType = NewType("PatternType", str)

# Infrastructure Layer (Rule 4: Isolate Impurity)

class NLPProcessor(Protocol):
    """Protocol for NLP processing implementations."""
    def process_sentences(self, text: str) -> List[SentenceText]:
        """Split text into sentences."""
        ...
    
    def extract_entities(self, sentence: str) -> List[EntityName]:
        """Extract entities from sentence."""
        ...
    
    def extract_predicates(self, sentence: str) -> List[PredicateName]:
        """Extract predicates from sentence."""
        ...

class SpacyNLPProcessor:
    """SpaCy-based NLP processor."""
    
    def __init__(self):
        """Initialize SpaCy processor."""
        self._nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load SpaCy model with fallback."""
        try:
            import spacy
            return spacy.load("en_core_web_sm")
        except (ImportError, OSError):
            return None
    
    def process_sentences(self, text: str) -> List[SentenceText]:
        """Split text into sentences using SpaCy."""
        if self._nlp:
            doc = self._nlp(text)
            return [SentenceText(sent.text.strip()) for sent in doc.sents if sent.text.strip()]
        return self._fallback_sentence_split(text)
    
    def _fallback_sentence_split(self, text: str) -> List[SentenceText]:
        """Fallback sentence splitting without SpaCy."""
        sentences = re.split(r'[.!?]+', text)
        return [SentenceText(s.strip()) for s in sentences if s.strip()]
    
    def extract_entities(self, sentence: str) -> List[EntityName]:
        """Extract entities using SpaCy NER."""
        if not self._nlp:
            return self._fallback_entity_extraction(sentence)
        
        doc = self._nlp(sentence)
        entities = [EntityName(ent.text.lower()) for ent in doc.ents]
        entities.extend([EntityName(chunk.text.lower()) for chunk in doc.noun_chunks])
        return self._filter_entities(list(set(entities)))
    
    def _fallback_entity_extraction(self, sentence: str) -> List[EntityName]:
        """Extract entities without SpaCy."""
        patterns = [
            r'\b(system|user|application|service|database|server|client)\b',
            r'\b(number|integer|value|data|input|output|request|response)\b',
            r'\b([a-z]+(?:_[a-z]+)*)\b'
        ]
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, sentence.lower())
            entities.extend([EntityName(m) for m in matches])
        return self._filter_entities(entities)
    
    def _filter_entities(self, entities: List[EntityName]) -> List[EntityName]:
        """Filter out short or common entities."""
        return [e for e in entities if len(e) > 2]
    
    def extract_predicates(self, sentence: str) -> List[PredicateName]:
        """Extract predicates using SpaCy."""
        if not self._nlp:
            return self._fallback_predicate_extraction(sentence)
        
        doc = self._nlp(sentence)
        predicates = [PredicateName(token.lemma_.lower()) 
                     for token in doc if token.pos_ in ['VERB', 'ADJ']]
        return self._filter_predicates(predicates)
    
    def _fallback_predicate_extraction(self, sentence: str) -> List[PredicateName]:
        """Extract predicates without SpaCy."""
        patterns = [
            r'\b(is|are|was|were|be|been|being)\s+(\w+)',
            r'\b(must|shall|should|will|can|may)\s+(\w+)',
            r'\b(\w+)(?:ed|ing|s)?\b'
        ]
        predicates = []
        for pattern in patterns:
            matches = re.findall(pattern, sentence.lower())
            predicates.extend(self._flatten_matches(matches))
        return self._filter_predicates([PredicateName(p) for p in predicates])
    
    def _flatten_matches(self, matches: List[Any]) -> List[str]:
        """Flatten regex match tuples."""
        flattened = []
        for match in matches:
            if isinstance(match, tuple):
                flattened.extend(match)
            else:
                flattened.append(match)
        return flattened
    
    def _filter_predicates(self, predicates: List[PredicateName]) -> List[PredicateName]:
        """Filter out common words from predicates."""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered = [p for p in predicates if p not in common_words and len(p) > 2]
        return list(set(filtered))

# Business Logic Layer (Pure Functions)

class DocumentSplitter:
    """
    Splits a document into sections based on headers.
    Rule 2: Implements a single, clear responsibility.
    """

    def __init__(self):
        """Initializes the splitter with a regex for section headers."""
        # Regex to find section headers (e.g., "1. Introduction", "SECTION 2", "Appendix A:")
        self._section_header_pattern = re.compile(
            r"^(?P<header>(?:[A-Z][a-zA-Z\s,]+[A-Z]|\d+(?:\.\d+)*\.?\s+[A-Z].*?))$",
            re.MULTILINE
        )

    def split_into_sections(self, document: str) -> List[Tuple[SectionTitle, SectionContent]]:
        """
        Splits the document content into sections.

        Args:
            document: The raw text of the document.

        Returns:
            A list of tuples, where each tuple contains the section title and its content.
            If no headers are found, returns a single section with a default title.
        """
        sections = []
        headers = list(self._section_header_pattern.finditer(document))

        if not headers:
            content = document.strip()
            if content:
                return [(SectionTitle("Default Section"), SectionContent(content))]
            return []

        last_pos = 0
        for i, match in enumerate(headers):
            header_text = SectionTitle(match.group("header").strip())
            start_pos = match.end()
            
            if i == 0 and match.start() > 0:
                content = document[0:match.start()].strip()
                if content:
                    sections.append((SectionTitle("Preamble"), SectionContent(content)))

            end_pos = headers[i + 1].start() if i + 1 < len(headers) else len(document)
            content_text = SectionContent(document[start_pos:end_pos].strip())

            if content_text:
                sections.append((header_text, content_text))
        
        return sections


class PatternRepository:
    """Repository for NLP patterns, optimized for single-pass matching."""

    @staticmethod
    def get_requirement_indicators() -> Dict[RequirementType, List[str]]:
        """Returns mapping of requirement types to indicator words."""
        return {
            RequirementType.CONSTRAINT: ["must", "shall", "required", "mandatory"],
            RequirementType.BEHAVIOR: ["when", "if", "upon", "during", "while"],
            RequirementType.PERFORMANCE: ["within", "seconds", "milliseconds", "response time", "throughput"],
            RequirementType.VALIDATION: ["validate", "verify", "check", "ensure", "confirm"],
            RequirementType.OUTPUT: ["output", "return", "display", "show", "report"],
            RequirementType.SECURITY: ["authenticate", "authorize", "secure", "access", "permission"],
            RequirementType.EXCEPTION: ["except", "unless", "however", "but", "special case"]
        }

    @staticmethod
    def get_quantifier_regex() -> str:
        """Returns a single regex for all logical quantifiers."""
        patterns = [
            r'for\s+(all|every)',
            r'(all|every|each|any|some|exists|forall)',
            r'([∀∃])'
        ]
        return r'\b(' + '|'.join(patterns) + r')\b'

    @staticmethod
    def get_conditional_regex() -> str:
        """Returns a single regex for all conditional statements."""
        patterns = [
            r'provided\s+that',
            r'given\s+that',
            r'whenever',
            r'if',
            r'when',
            r'then',
            r'implies',
            r'therefore',
            r'consequently'
        ]
        return r'\b(' + '|'.join(patterns) + r')\b'

    @staticmethod
    def get_logical_operator_regex() -> str:
        """Returns a single regex for all logical operators."""
        patterns = [
            r'and',
            r'or',
            r'not',
            r'xor',
            r'nand',
            r'nor',
            r'[∧∨¬⊕⊼⊽]'
        ]
        return r'\b(' + '|'.join(patterns) + r')\b'

    @staticmethod
    def get_temporal_regex() -> str:
        """Returns a single regex for all temporal logic operators."""
        return r'\b(always|eventually|never|until|before|after|while)\b'

    @staticmethod
    def get_mathematical_patterns() -> List[Tuple[str, PatternType]]:
        """Returns regex patterns for mathematical constraints."""
        return [
            (r'\b(\w+)\s+is\s+(?:a\s+)?prime\b', "prime"),
            (r'\b(\w+)\s+is\s+even\b', "even"),
            (r'\b(\w+)\s+is\s+odd\b', "odd"),
            (r'(\w+)\s+(?:is|equals?|=)\s+([\w\.]+)\b', "equality"),
            (r'(\w+)\s+(?:is\s+)?(?:greater\s+than?|>)\s+([\w\.]+)\b', "greater_than"),
            (r'(\w+)\s+(?:is\s+)?(?:less\s+than?|<)\s+([\w\.]+)\b', "less_than")
        ]

    @staticmethod
    def get_ambiguous_words() -> List[str]:
        """Returns a list of words that indicate ambiguity."""
        return ['properly', 'appropriately', 'suitable', 'adequate', 'reasonable', 'appropriate']

    @staticmethod
    def get_formal_language_indicators() -> List[str]:
        """Returns a list of words indicating formal language."""
        return ['must', 'shall', 'should', 'required', 'specified']

class RequirementClassifier:
    """Classifies requirements by type based on keyword indicators."""

    def __init__(self, indicators: Dict[RequirementType, List[str]]):
        """Initialize with requirement indicators."""
        self._indicators = indicators

    def classify(self, sentence: SentenceText) -> RequirementType:
        """Classify requirement type based on indicators. Rule 2: Orchestrator."""
        type_scores = self._calculate_type_scores(sentence)
        if not type_scores:
            return RequirementType.CONSTRAINT
        return max(type_scores.items(), key=lambda item: item[1])[0]

    def _calculate_type_scores(self, sentence: SentenceText) -> Dict[RequirementType, int]:
        """Calculate scores for each requirement type. Rule 2: Implementation."""
        scores = defaultdict(int)
        sentence_lower = sentence.lower()
        for req_type, indicators in self._indicators.items():
            for indicator in indicators:
                if indicator in sentence_lower:
                    scores[req_type] += 1
        return scores

class LogicalAnalyzer:
    """Analyzes logical structure of sentences using a single-pass strategy."""

    def __init__(self, pattern_repo: PatternRepository):
        """Initialize and pre-compile regex patterns for efficiency."""
        self._quantifier_re = re.compile(pattern_repo.get_quantifier_regex(), re.IGNORECASE)
        self._conditional_re = re.compile(pattern_repo.get_conditional_regex(), re.IGNORECASE)
        self._operator_re = re.compile(pattern_repo.get_logical_operator_regex(), re.IGNORECASE)
        self._temporal_re = re.compile(pattern_repo.get_temporal_regex(), re.IGNORECASE)

    def analyze(self, sentence: SentenceText) -> LogicalStructure:
        """Analyze sentence for logical structure. Rule 2: Structure for Scannability."""
        return LogicalStructure(
            quantifiers=self._find_matches(sentence, self._quantifier_re),
            conditionals=self._find_matches(sentence, self._conditional_re),
            logical_operators=self._find_matches(sentence, self._operator_re),
            temporal_operators=self._find_matches(sentence, self._temporal_re),
        )

    def _find_matches(self, sentence: SentenceText, compiled_regex: re.Pattern) -> List[str]:
        """Finds all matches using a single pre-compiled regex."""
        matches = [match.group(1) for match in compiled_regex.finditer(sentence)]
        normalized_matches = [m.split()[-1] for m in matches]
        return sorted(list(set(normalized_matches)))

class ConstraintExtractor:
    """Extracts formal constraints from sentences."""

    def __init__(self, pattern_repo: PatternRepository):
        """Initialize with pattern repository."""
        self._patterns = pattern_repo

    def extract(
        self,
        sentence: SentenceText,
        entities: List[EntityName],
        predicates: List[PredicateName]
    ) -> List[FormalConstraint]:
        """Extract formal constraints from sentence."""
        constraints = []
        for pattern, constraint_type in self._patterns.get_mathematical_patterns():
            for match in re.finditer(pattern, sentence.lower()):
                constraint = self._create_constraint(match, constraint_type)
                if constraint:
                    constraints.append(constraint)
        return constraints

    def _create_constraint(self, match: re.Match, constraint_type: str) -> Optional[FormalConstraint]:
        """Create constraint from regex match."""
        groups = match.groups()
        var_name = groups[0]
        if len(groups) > 1:
            return self._create_binary_constraint(var_name, groups[1], constraint_type)
        return self._create_unary_constraint(var_name, constraint_type)

    def _create_unary_constraint(self, var_name: str, constraint_type: str) -> FormalConstraint:
        """Create unary constraint."""
        return FormalConstraint(
            constraint_type=constraint_type,
            variables=[var_name],
            predicates=[constraint_type],
            logical_form=LogicalFormula(f"{constraint_type}({var_name})"),
            confidence=ConfidenceScore(0.8)
        )

    def _create_binary_constraint(self, var_name: str, value: str, constraint_type: str) -> FormalConstraint:
        """Create binary constraint."""
        return FormalConstraint(
            constraint_type=constraint_type,
            variables=[var_name],
            predicates=[constraint_type],
            logical_form=LogicalFormula(f"{constraint_type}({var_name}, {value})"),
            confidence=ConfidenceScore(0.8)
        )

class ConfidenceCalculator:
    """Calculates confidence score for requirement extraction."""
    BASE_SCORE = 0.5
    ENTITY_BONUS = 0.1
    PREDICATE_BONUS = 0.1
    QUANTIFICATION_BONUS = 0.05
    CONDITIONAL_BONUS = 0.05
    AMBIGUITY_PENALTY = -0.1
    FORMAL_LANGUAGE_BONUS = 0.1

    def calculate(
        self,
        entities: List[EntityName],
        predicates: List[PredicateName],
        logical_structure: LogicalStructure,
        sentence: SentenceText,
        ambiguous_words: List[str],
        formal_indicators: List[str]
    ) -> ConfidenceScore:
        """Calculate confidence score based on various factors."""
        score = self.BASE_SCORE
        score += self._calculate_entity_bonus(entities)
        score += self._calculate_predicate_bonus(predicates)
        score += self._calculate_quantification_bonus(logical_structure.quantifiers)
        score += self._calculate_conditional_bonus(logical_structure.conditionals)
        score += self._calculate_ambiguity_penalty(sentence, ambiguous_words)
        # score += self._calculate_formal_language_bonus(sentence, formal_indicators)
        return ConfidenceScore(max(0.0, min(1.0, score)))

    def _calculate_entity_bonus(self, entities: List[EntityName]) -> float:
        """Calculate bonus for found entities."""
        return self.ENTITY_BONUS * len(entities)

    def _calculate_predicate_bonus(self, predicates: List[PredicateName]) -> float:
        """Calculate bonus for found predicates."""
        return self.PREDICATE_BONUS * len(predicates)

    def _calculate_quantification_bonus(self, quantifiers: List[str]) -> float:
        """Calculate bonus for found quantifiers."""
        return self.QUANTIFICATION_BONUS * len(quantifiers)

    def _calculate_conditional_bonus(self, conditionals: List[str]) -> float:
        """Calculate bonus for found conditionals."""
        return self.CONDITIONAL_BONUS * len(conditionals)

    def _calculate_ambiguity_penalty(self, sentence: SentenceText, ambiguous_words: List[str]) -> float:
        """Calculate penalty for ambiguous words."""
        penalty = 0.0
        for word in ambiguous_words:
            if word in sentence.lower():
                penalty += self.AMBIGUITY_PENALTY
        return penalty

    def _calculate_formal_language_bonus(self, sentence: SentenceText, formal_indicators: List[str]) -> float:
        """Calculate bonus for formal language indicators."""
        bonus = 0.0
        for indicator in formal_indicators:
            if indicator in sentence.lower():
                bonus += self.FORMAL_LANGUAGE_BONUS
        return bonus

class SectionCategorizer:
    """
    Categorizes document sections based on their titles.
    """

    _CATEGORY_KEYWORDS: ClassVar[Dict[RequirementCategory, List[str]]] = {
        RequirementCategory.FUNCTIONAL: [
            "functional requirements",
            "features",
            "system behavior",
        ],
        RequirementCategory.NON_FUNCTIONAL: [
            "non-functional",
            "quality attributes",
            "performance",
            "security",
            "usability",
        ],
        RequirementCategory.UI_UX: ["user interface", "ui", "ux", "user experience", "gui"],
    }

    def categorize(self, section_title: SectionTitle) -> RequirementCategory:
        """
        Categorizes a section title into a RequirementCategory.

        Uses keyword matching against a predefined dictionary to classify the
        section. Defaults to 'UNCATEGORIZED' if no match is found.
        """
        normalized_title = section_title.lower()
        for category, keywords in self._CATEGORY_KEYWORDS.items():
            if any(keyword in normalized_title for keyword in keywords):
                return category
        return RequirementCategory.UNCATEGORIZED

class RequirementAnalysisService:
    """
    Orchestrates the detailed analysis of a single sentence or text block.
    Rule 2: Orchestrator class.
    """

    def __init__(
        self,
        nlp_processor: NLPProcessor,
        classifier: RequirementClassifier,
        logical_analyzer: LogicalAnalyzer,
        constraint_extractor: ConstraintExtractor,
        confidence_calculator: ConfidenceCalculator,
        pattern_repo: PatternRepository,
    ):
        """Initializes the service with all necessary components (dependencies)."""
        self._nlp = nlp_processor
        self._classifier = classifier
        self._logical_analyzer = logical_analyzer
        self._constraint_extractor = constraint_extractor
        self._confidence_calculator = confidence_calculator
        self._pattern_repo = pattern_repo

    def analyze_sentence_to_item(self, sentence: SentenceText) -> Optional[RequirementItem]:
        """
        Analyzes a single sentence and transforms it into a structured RequirementItem.
        This is a high-level policy method.
        """
        if not self._is_sentence_substantive(sentence):
            return None

        entities = self._extract_entities_from_sentence(sentence)
        predicates = self._extract_predicates_from_sentence(sentence)
        logical_structure = self._analyze_logical_structure_of_sentence(sentence)

        return RequirementItem(
            raw_text=RequirementText(sentence),
            type=self._classify_requirement_type_for_sentence(sentence),
            category=RequirementCategory.UNCATEGORIZED,  # Category is handled higher up
            entities=entities,
            predicates=predicates,
            logical_structure=logical_structure,
            formal_constraints=self._extract_constraints_from_sentence(sentence, entities, predicates),
            confidence=self._calculate_confidence_for_analysis(
                sentence, entities, predicates, logical_structure
            ),
        )

    def _is_sentence_substantive(self, sentence: SentenceText) -> bool:
        """Checks if a sentence is long enough to be meaningful."""
        return len(sentence.strip()) >= 10

    def _extract_entities_from_sentence(self, sentence: SentenceText) -> List[EntityName]:
        """Extracts entities using the NLP processor."""
        return self._nlp.extract_entities(sentence)

    def _extract_predicates_from_sentence(self, sentence: SentenceText) -> List[PredicateName]:
        """Extracts predicates using the NLP processor."""
        return self._nlp.extract_predicates(sentence)
    
    def _analyze_logical_structure_of_sentence(self, sentence: SentenceText) -> LogicalStructure:
        """Analyzes the logical structure of the sentence."""
        return self._logical_analyzer.analyze(sentence)

    def _classify_requirement_type_for_sentence(self, sentence: SentenceText) -> RequirementType:
        """Classifies the requirement type of the sentence."""
        return self._classifier.classify(sentence)

    def _extract_constraints_from_sentence(
        self, sentence: SentenceText, entities: List[EntityName], predicates: List[PredicateName]
    ) -> List[FormalConstraint]:
        """Extracts formal constraints from the sentence."""
        return self._constraint_extractor.extract(sentence, entities, predicates)

    def _calculate_confidence_for_analysis(
        self,
        sentence: SentenceText,
        entities: List[EntityName],
        predicates: List[PredicateName],
        logical_structure: LogicalStructure,
    ) -> ConfidenceScore:
        """Calculates the confidence score for the analysis."""
        return self._confidence_calculator.calculate(
            entities=entities,
            predicates=predicates,
            logical_structure=logical_structure,
            sentence=sentence,
            ambiguous_words=self._pattern_repo.get_ambiguous_words(),
            formal_indicators=self._pattern_repo.get_formal_language_indicators(),
        )


class RequirementsAnalyzer:
    """
    Main facade for extracting structured requirements from natural language documents.
    Rule 2: Orchestrator, this is the main public-facing class.
    """

    def __init__(self, analysis_service: RequirementAnalysisService):
        """Initializes the analyzer with its dependent services."""
        self._analysis_service = analysis_service
        self._document_splitter = DocumentSplitter()
        self._section_categorizer = SectionCategorizer()

    def analyze_document_to_requirements(self, document: str) -> List[RequirementItem]:
        """
        Analyzes a full document, splitting it into sections and processing each.
        This is the primary public method.
        """
        requirement_items = []
        sections = self._document_splitter.split_into_sections(document)

        for title, content in sections:
            category = self._section_categorizer.categorize(title)
            # A more robust sentence splitter than just '.'
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
            for sentence in sentences:
                if not sentence or not sentence.strip():
                    continue
                if item := self._analysis_service.analyze_sentence_to_item(SentenceText(sentence.strip())):
                    # Update category post-analysis
                    updated_item = self._update_item_with_category(item, category)
                    requirement_items.append(updated_item)
        
        return requirement_items

    def _update_item_with_category(self, item: RequirementItem, category: RequirementCategory) -> RequirementItem:
        """Creates a new RequirementItem with an updated category."""
        return RequirementItem(
            raw_text=item.raw_text,
            type=item.type,
            category=category,
            entities=item.entities,
            predicates=item.predicates,
            logical_structure=item.logical_structure,
            formal_constraints=item.formal_constraints,
            confidence=item.confidence,
        )

# Factory Function (Dependency Injection Root)
# Rule 4: Isolates Impurity. The creation of concrete infrastructure objects happens here.

def create_requirements_analyzer() -> RequirementsAnalyzer:
    """
    Constructs the full RequirementsAnalyzer with its dependencies.
    This is the DI container for the application.
    """
    # 1. Infrastructure Layer
    nlp_processor = SpacyNLPProcessor()
    pattern_repo = PatternRepository()

    # 2. Business Logic Layer
    classifier = RequirementClassifier(pattern_repo.get_requirement_indicators())
    logical_analyzer = LogicalAnalyzer(pattern_repo)
    constraint_extractor = ConstraintExtractor(pattern_repo)
    confidence_calculator = ConfidenceCalculator()

    # 3. Service Layer
    analysis_service = RequirementAnalysisService(
        nlp_processor=nlp_processor,
        classifier=classifier,
        logical_analyzer=logical_analyzer,
        constraint_extractor=constraint_extractor,
        confidence_calculator=confidence_calculator,
        pattern_repo=pattern_repo,
    )

    # 4. Application Facade
    analyzer = RequirementsAnalyzer(analysis_service=analysis_service)
    
    return analyzer