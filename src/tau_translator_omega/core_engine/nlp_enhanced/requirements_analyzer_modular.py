"""
Modular Requirements Analyzer following the Intentional Disclosure Principle.

Main API that composes all the smaller modules into a cohesive analyzer.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List
from .requirements import (
    RequirementItem, RequirementText, PatternRepository,
    SpacyNLPProcessor, DocumentSplitter, RequirementClassifier,
    LogicalAnalyzer, ConstraintExtractor, SectionCategorizer,
    RequirementAnalysisService
)


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


def create_requirements_analyzer() -> RequirementsAnalyzer:
    """Factory function to create a requirements analyzer."""
    return RequirementsAnalyzer()