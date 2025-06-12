"""
Service layer for requirements analysis orchestration.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional
from .domain_types import (
    RequirementText, SentenceText, RequirementItem,
    EntityName, PredicateName
)
from .nlp_processor import NLPProcessor
from .analyzers import (
    RequirementClassifier, LogicalAnalyzer, 
    ConstraintExtractor, ConfidenceCalculator
)


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