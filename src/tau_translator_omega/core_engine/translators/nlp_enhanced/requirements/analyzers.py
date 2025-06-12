"""
Business logic analyzers for requirements processing.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
from .domain_types import (
    RequirementType, SentenceText, SectionTitle, SectionContent,
    EntityName, PredicateName, ConfidenceScore, LogicalFormula,
    LogicalStructure, FormalConstraint
)
from .pattern_repository import PatternRepository


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