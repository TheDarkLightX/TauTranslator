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

from typing import Dict, List, Optional, Set, Any, Tuple, NewType, Protocol
from dataclasses import dataclass, field
from enum import Enum, auto
import re
from collections import defaultdict

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

class RequirementType(Enum):
    """Types of requirements that can be extracted."""
    CONSTRAINT = auto()
    BEHAVIOR = auto()
    PERFORMANCE = auto()
    VALIDATION = auto()
    OUTPUT = auto()
    SECURITY = auto()
    EXCEPTION = auto()

@dataclass(frozen=True)
class LogicalStructure:
    """Represents the logical structure of a requirement."""
    quantifiers: List[str] = field(default_factory=list)
    conditionals: List[str] = field(default_factory=list)
    logical_operators: List[str] = field(default_factory=list)
    temporal_operators: List[str] = field(default_factory=list)
    
    @property
    def has_quantification(self) -> bool:
        """Check if structure has quantification."""
        return len(self.quantifiers) > 0
    
    @property
    def has_conditionals(self) -> bool:
        """Check if structure has conditionals."""
        return len(self.conditionals) > 0
    
    @property
    def has_temporal(self) -> bool:
        """Check if structure has temporal operators."""
        return len(self.temporal_operators) > 0

@dataclass(frozen=True)
class FormalConstraint:
    """Represents a formal constraint extracted from requirements."""
    constraint_type: str
    variables: List[str]
    predicates: List[str]
    logical_form: LogicalFormula
    confidence: ConfidenceScore

@dataclass(frozen=True)
class RequirementItem:
    """Represents a single extracted requirement."""
    raw_text: RequirementText
    type: RequirementType
    category: str
    entities: List[EntityName]
    predicates: List[PredicateName]
    logical_structure: LogicalStructure
    formal_constraints: List[FormalConstraint]
    confidence: ConfidenceScore
    
    @property
    def has_quantification(self) -> bool:
        """Check if requirement has quantification."""
        return self.logical_structure.has_quantification

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

class PatternRepository:
    """Repository of linguistic patterns for requirement analysis."""
    
    @staticmethod
    def get_requirement_indicators() -> Dict[RequirementType, List[str]]:
        """Get indicators for each requirement type."""
        return {
            RequirementType.CONSTRAINT: ["must", "shall", "should", "required", "mandatory"],
            RequirementType.BEHAVIOR: ["when", "if", "upon", "during", "while"],
            RequirementType.PERFORMANCE: ["within", "seconds", "milliseconds", "response time", "throughput"],
            RequirementType.VALIDATION: ["validate", "verify", "check", "ensure", "confirm"],
            RequirementType.OUTPUT: ["output", "return", "display", "show", "report"],
            RequirementType.SECURITY: ["authenticate", "authorize", "secure", "access", "permission"],
            RequirementType.EXCEPTION: ["except", "unless", "however", "but", "special case"]
        }
    
    @staticmethod
    def get_quantifier_patterns() -> List[str]:
        """Get quantifier regex patterns."""
        return [
            r'\b(all|every|each|any|some|for all|for every)\b',
            r'\b(∀|∃|forall|exists)\b',
            r'\bfor\s+any\s+(\w+)\b'
        ]
    
    @staticmethod
    def get_conditional_patterns() -> List[str]:
        """Get conditional regex patterns."""
        return [
            r'\b(if|when|whenever|provided that|given that)\b',
            r'\b(then|implies|therefore|consequently)\b'
        ]
    
    @staticmethod
    def get_logical_operator_patterns() -> List[str]:
        """Get logical operator regex patterns."""
        return [
            r'\b(and|or|not|but|except|unless)\b',
            r'[∧∨¬→↔]'
        ]
    
    @staticmethod
    def get_temporal_patterns() -> List[str]:
        """Get temporal regex patterns."""
        return [
            r'\b(before|after|during|while|until|since)\b',
            r'\b(within \d+|in \d+|after \d+)\s*(seconds?|minutes?|hours?|milliseconds?)\b'
        ]
    
    @staticmethod
    def get_mathematical_patterns() -> List[Tuple[str, str]]:
        """Get mathematical constraint patterns."""
        return [
            (r'(\w+)\s+(?:is|equals?|=)\s+(\d+)', 'equality'),
            (r'(\w+)\s+(?:is\s+)?(?:greater\s+than?|>)\s+(\d+)', 'greater_than'),
            (r'(\w+)\s+(?:is\s+)?(?:less\s+than?|<)\s+(\d+)', 'less_than'),
            (r'(\w+)\s+(?:is\s+)?prime', 'prime'),
            (r'(\w+)\s+(?:is\s+)?even', 'even'),
            (r'(\w+)\s+(?:is\s+)?odd', 'odd')
        ]

class DocumentSplitter:
    """Splits documents into sections and sentences."""
    
    @staticmethod
    def split_into_sections(document: str) -> List[Tuple[SectionTitle, SectionContent]]:
        """Split document into sections with headers."""
        sections = []
        current_section = SectionTitle("General")
        current_content = []
        
        for line in document.split('\n'):
            if DocumentSplitter._is_section_header(line):
                sections = DocumentSplitter._save_current_section(
                    sections, current_section, current_content
                )
                current_section = SectionTitle(line.strip())
                current_content = []
            elif line.strip():
                current_content.append(line.strip())
        
        return DocumentSplitter._save_current_section(
            sections, current_section, current_content
        )
    
    @staticmethod
    def _is_section_header(line: str) -> bool:
        """Check if line is a section header."""
        line = line.strip()
        if not line:
            return False
        return (re.match(r'^\d+\.', line) or 
                line.isupper() or 
                (line.istitle() and len(line.split()) <= 5))
    
    @staticmethod
    def _save_current_section(
        sections: List[Tuple[SectionTitle, SectionContent]], 
        title: SectionTitle, 
        content: List[str]
    ) -> List[Tuple[SectionTitle, SectionContent]]:
        """Save current section if it has content."""
        if content:
            sections.append((title, SectionContent(' '.join(content))))
        return sections

class RequirementClassifier:
    """Classifies requirements by type."""
    
    def __init__(self, indicators: Dict[RequirementType, List[str]]):
        """Initialize with requirement indicators."""
        self._indicators = indicators
    
    def classify(self, sentence: SentenceText) -> RequirementType:
        """Classify requirement type based on indicators."""
        type_scores = self._calculate_type_scores(sentence)
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return RequirementType.CONSTRAINT
    
    def _calculate_type_scores(self, sentence: SentenceText) -> Dict[RequirementType, int]:
        """Calculate scores for each requirement type."""
        sentence_lower = sentence.lower()
        scores = defaultdict(int)
        
        for req_type, indicators in self._indicators.items():
            for indicator in indicators:
                if indicator in sentence_lower:
                    scores[req_type] += 1
        
        return dict(scores)

class LogicalAnalyzer:
    """Analyzes logical structure of sentences."""
    
    def __init__(self, pattern_repo: PatternRepository):
        """Initialize with pattern repository."""
        self._patterns = pattern_repo
    
    def analyze(self, sentence: SentenceText) -> LogicalStructure:
        """Analyze logical structure of sentence."""
        return LogicalStructure(
            quantifiers=self._extract_quantifiers(sentence),
            conditionals=self._extract_conditionals(sentence),
            logical_operators=self._extract_logical_operators(sentence),
            temporal_operators=self._extract_temporal_operators(sentence)
        )
    
    def _extract_quantifiers(self, sentence: SentenceText) -> List[str]:
        """Extract quantifiers from sentence."""
        return self._extract_patterns(sentence, self._patterns.get_quantifier_patterns())
    
    def _extract_conditionals(self, sentence: SentenceText) -> List[str]:
        """Extract conditionals from sentence."""
        return self._extract_patterns(sentence, self._patterns.get_conditional_patterns())
    
    def _extract_logical_operators(self, sentence: SentenceText) -> List[str]:
        """Extract logical operators from sentence."""
        return self._extract_patterns(sentence, self._patterns.get_logical_operator_patterns())
    
    def _extract_temporal_operators(self, sentence: SentenceText) -> List[str]:
        """Extract temporal operators from sentence."""
        return self._extract_patterns(sentence, self._patterns.get_temporal_patterns())
    
    def _extract_patterns(self, sentence: SentenceText, patterns: List[str]) -> List[str]:
        """Extract matches for given patterns."""
        matches = []
        sentence_lower = sentence.lower()
        for pattern in patterns:
            found = re.findall(pattern, sentence_lower)
            matches.extend(found)
        return matches

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
            matches = re.findall(pattern, sentence.lower())
            for match in matches:
                constraint = self._create_constraint(match, constraint_type)
                if constraint:
                    constraints.append(constraint)
        
        return constraints
    
    def _create_constraint(self, match: Any, constraint_type: str) -> Optional[FormalConstraint]:
        """Create constraint from regex match."""
        if not isinstance(match, tuple):
            return self._create_unary_constraint(match, constraint_type)
        
        var_name = match[0]
        if len(match) > 1:
            return self._create_binary_constraint(var_name, match[1], constraint_type)
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
    """Calculates confidence scores for requirements."""
    
    @staticmethod
    def calculate(
        sentence: SentenceText,
        entities: List[EntityName],
        predicates: List[PredicateName],
        logical_structure: LogicalStructure
    ) -> ConfidenceScore:
        """Calculate confidence score for requirement extraction."""
        score = 0.5  # Base score
        
        score = ConfidenceCalculator._add_structure_points(score, entities, predicates, logical_structure)
        score = ConfidenceCalculator._add_formality_points(score, sentence)
        score = ConfidenceCalculator._subtract_ambiguity_points(score, sentence)
        
        return ConfidenceScore(max(0.0, min(1.0, score)))
    
    @staticmethod
    def _add_structure_points(
        score: float,
        entities: List[EntityName],
        predicates: List[PredicateName],
        logical_structure: LogicalStructure
    ) -> float:
        """Add points for clear structure."""
        if entities:
            score += 0.1
        if predicates:
            score += 0.1
        if logical_structure.has_quantification:
            score += 0.1
        if logical_structure.has_conditionals:
            score += 0.1
        return score
    
    @staticmethod
    def _add_formality_points(score: float, sentence: SentenceText) -> float:
        """Add points for formal language."""
        formal_indicators = ['must', 'shall', 'should', 'required', 'specified']
        sentence_lower = sentence.lower()
        
        for indicator in formal_indicators:
            if indicator in sentence_lower:
                score += 0.05
        
        return score
    
    @staticmethod
    def _subtract_ambiguity_points(score: float, sentence: SentenceText) -> float:
        """Subtract points for ambiguous language."""
        ambiguous_words = ['properly', 'appropriately', 'suitable', 'adequate', 'reasonable']
        sentence_lower = sentence.lower()
        
        for word in ambiguous_words:
            if word in sentence_lower:
                score -= 0.1
        
        return score

class SectionCategorizer:
    """Categorizes requirements based on section titles."""
    
    @staticmethod
    def categorize(section_title: SectionTitle) -> str:
        """Categorize requirement based on section title."""
        category_keywords = {
            'validation': ['validation', 'input', 'verify'],
            'verification': ['verification', 'prime', 'check'],
            'output': ['output', 'display', 'return'],
            'performance': ['performance', 'time', 'speed'],
            'security': ['security', 'authentication', 'access'],
            'behavior': ['behavior', 'system', 'operation']
        }
        
        title_lower = section_title.lower()
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'

# Service Layer (Orchestration)

class RequirementAnalysisService:
    """Orchestrates requirement analysis operations."""
    
    def __init__(
        self,
        nlp_processor: NLPProcessor,
        classifier: RequirementClassifier,
        logical_analyzer: LogicalAnalyzer,
        constraint_extractor: ConstraintExtractor
    ):
        """Initialize with analysis components."""
        self._nlp = nlp_processor
        self._classifier = classifier
        self._logical_analyzer = logical_analyzer
        self._constraint_extractor = constraint_extractor
    
    def analyze_sentence(self, sentence: SentenceText) -> Optional[RequirementItem]:
        """Analyze single sentence for requirements."""
        if len(sentence.strip()) < 10:
            return None
        
        req_type = self._classifier.classify(sentence)
        entities = self._nlp.extract_entities(sentence)
        predicates = self._nlp.extract_predicates(sentence)
        logical_structure = self._logical_analyzer.analyze(sentence)
        formal_constraints = self._constraint_extractor.extract(sentence, entities, predicates)
        confidence = ConfidenceCalculator.calculate(sentence, entities, predicates, logical_structure)
        
        return RequirementItem(
            raw_text=RequirementText(sentence),
            type=req_type,
            category="general",
            entities=entities,
            predicates=predicates,
            logical_structure=logical_structure,
            formal_constraints=formal_constraints,
            confidence=confidence
        )
    
    def analyze_text(self, text: str) -> List[RequirementItem]:
        """Analyze text for requirements."""
        sentences = self._nlp.process_sentences(text)
        requirements = []
        
        for sentence in sentences:
            req_item = self.analyze_sentence(sentence)
            if req_item:
                requirements.append(req_item)
        
        return requirements

class RequirementsAnalyzer:
    """Main analyzer for extracting structured requirements from natural language."""
    
    def __init__(self):
        """Initialize the requirements analyzer."""
        # Initialize components
        pattern_repo = PatternRepository()
        nlp_processor = SpacyNLPProcessor()
        
        # Initialize business logic
        classifier = RequirementClassifier(pattern_repo.get_requirement_indicators())
        logical_analyzer = LogicalAnalyzer(pattern_repo)
        constraint_extractor = ConstraintExtractor(pattern_repo)
        
        # Initialize service
        self._analysis_service = RequirementAnalysisService(
            nlp_processor, classifier, logical_analyzer, constraint_extractor
        )
        self._document_splitter = DocumentSplitter()
        self._section_categorizer = SectionCategorizer()
    
    def extract_requirements(self, text: str) -> List[RequirementItem]:
        """Extract structured requirements from natural language text."""
        return self._analysis_service.analyze_text(text)
    
    def extract_requirements_from_document(self, document: str) -> List[RequirementItem]:
        """Extract requirements from a complete requirements document."""
        requirements = []
        sections = self._document_splitter.split_into_sections(document)
        
        for section_title, section_content in sections:
            section_requirements = self.extract_requirements(section_content)
            category = self._section_categorizer.categorize(section_title)
            
            for req in section_requirements:
                # Create new requirement with updated category
                requirements.append(self._update_requirement_category(req, category))
        
        return requirements
    
    def _update_requirement_category(self, req: RequirementItem, category: str) -> RequirementItem:
        """Create new requirement item with updated category."""
        return RequirementItem(
            raw_text=req.raw_text,
            type=req.type,
            category=category,
            entities=req.entities,
            predicates=req.predicates,
            logical_structure=req.logical_structure,
            formal_constraints=req.formal_constraints,
            confidence=req.confidence
        )

# Factory function
def create_requirements_analyzer() -> RequirementsAnalyzer:
    """Factory function to create a requirements analyzer."""
    return RequirementsAnalyzer()