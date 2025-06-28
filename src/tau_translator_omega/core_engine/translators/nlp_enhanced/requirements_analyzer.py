#!/usr/bin/env python3
"""
Requirements Analyzer for Natural Language Processing
===================================================

Advanced analysis of natural language requirements documents for conversion
to formal Tau Language specifications.

Features:
- Multi-sentence requirement extraction
- Requirement type classification (constraints, behaviors, performance)
- Entity and predicate identification
- Logical structure analysis
- Temporal constraint detection
- Exception and edge case handling
"""

from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import re
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    spacy = None
    SPACY_AVAILABLE = False
from collections import defaultdict

from .amr_semantic_layer import AMRSemanticAnalyzer, AMRGraph
from .requirements_models import (
    RequirementType,
    LogicalStructure,
    FormalConstraint,
    RequirementItem,
)


class RequirementsAnalyzer:
    """
    Main analyzer for extracting structured requirements from natural language.
    
    Uses advanced NLP techniques including:
    - Named entity recognition
    - Dependency parsing
    - Semantic role labeling
    - Temporal expression extraction
    """
    
    def __init__(self):
        """Initialize the requirements analyzer"""
        if SPACY_AVAILABLE:
            try:
                # Try to load spaCy model, fall back to simple processing if not available
                self.nlp = spacy.load("en_core_web_sm")
                self.use_spacy = True
            except OSError:
                self.nlp = None
                self.use_spacy = False
        else:
            self.nlp = None
            self.use_spacy = False
            
        self.amr_analyzer = AMRSemanticAnalyzer()
        
        # Requirement type indicators
        self.requirement_indicators = {
            RequirementType.CONSTRAINT: ["must", "shall", "should", "required", "mandatory"],
            RequirementType.BEHAVIOR: ["when", "if", "upon", "during", "while"],
            RequirementType.PERFORMANCE: ["within", "seconds", "milliseconds", "response time", "throughput"],
            RequirementType.VALIDATION: ["validate", "verify", "check", "ensure", "confirm"],
            RequirementType.OUTPUT: ["output", "return", "display", "show", "report"],
            RequirementType.SECURITY: ["authenticate", "authorize", "secure", "access", "permission"],
            RequirementType.EXCEPTION: ["except", "unless", "however", "but", "special case"]
        }
        
        # Logical structure patterns
        self.quantifier_patterns = [
            r'\b(all|every|each|any|some|for all|for every)\b',
            r'\b(∀|∃|forall|exists)\b',
            r'\bfor\s+any\s+(\w+)\b'  # "for any integer n"
        ]
        
        self.conditional_patterns = [
            r'\b(if|when|whenever|provided that|given that)\b',
            r'\b(then|implies|therefore|consequently)\b'
        ]
        
        self.logical_operator_patterns = [
            r'\b(and|or|not|but|except|unless)\b',
            r'[∧∨¬→↔]'
        ]
        
        self.temporal_patterns = [
            r'\b(before|after|during|while|until|since)\b',
            r'\b(within \d+|in \d+|after \d+)\s*(seconds?|minutes?|hours?|milliseconds?)\b'
        ]
    
    def extract_requirements(self, text: str) -> List[RequirementItem]:
        """
        Extract structured requirements from natural language text.
        
        Args:
            text: Natural language requirements text
            
        Returns:
            List of extracted requirement items
        """
        requirements = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        for sentence in sentences:
            req_item = self._analyze_sentence(sentence)
            if req_item:
                requirements.append(req_item)
        
        return requirements
    
    def extract_requirements_from_document(self, document: str) -> List[RequirementItem]:
        """
        Extract requirements from a complete requirements document.
        
        Handles multi-paragraph documents with section headers.
        """
        requirements = []
        
        # Split document into sections
        sections = self._split_into_sections(document)
        
        for section_title, section_content in sections:
            section_requirements = self.extract_requirements(section_content)
            
            # Add section context to requirements
            for req in section_requirements:
                req.category = self._categorize_from_section(section_title)
                
            requirements.extend(section_requirements)
        
        return requirements
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into individual sentences"""
        if self.use_spacy and self.nlp:
            doc = self.nlp(text)
            return [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            # Simple sentence splitting
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
    
    def _split_into_sections(self, document: str) -> List[Tuple[str, str]]:
        """Split document into sections with headers"""
        sections = []
        current_section = "General"
        current_content = []
        
        lines = document.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line is a section header (contains numbers or is all caps/title case)
            if (re.match(r'^\d+\.', line) or 
                line.isupper() or 
                (line.istitle() and len(line.split()) <= 5)):
                
                # Save previous section
                if current_content:
                    sections.append((current_section, ' '.join(current_content)))
                
                # Start new section
                current_section = line
                current_content = []
            else:
                current_content.append(line)
        
        # Add final section
        if current_content:
            sections.append((current_section, ' '.join(current_content)))
        
        return sections
    
    def _analyze_sentence(self, sentence: str) -> Optional[RequirementItem]:
        """Analyze a single sentence for requirement extraction"""
        if len(sentence.strip()) < 10:  # Skip very short sentences
            return None
        
        # Determine requirement type
        req_type = self._classify_requirement_type(sentence)
        
        # Extract entities and predicates
        entities = self._extract_entities(sentence)
        predicates = self._extract_predicates(sentence)
        
        # Analyze logical structure
        logical_structure = self._analyze_logical_structure(sentence)
        
        # Extract formal constraints
        formal_constraints = self._extract_formal_constraints(sentence, entities, predicates)
        
        # Calculate confidence
        confidence = self._calculate_confidence(sentence, entities, predicates, logical_structure)
        
        return RequirementItem(
            raw_text=sentence,
            type=req_type,
            category="general",
            entities=entities,
            predicates=predicates,
            logical_structure=logical_structure,
            formal_constraints=formal_constraints,
            confidence=confidence,
            has_quantification=logical_structure.has_quantification
        )
    
    def _classify_requirement_type(self, sentence: str) -> RequirementType:
        """Classify the type of requirement based on linguistic patterns"""
        sentence_lower = sentence.lower()
        
        # Score each requirement type
        type_scores = defaultdict(int)
        
        for req_type, indicators in self.requirement_indicators.items():
            for indicator in indicators:
                if indicator in sentence_lower:
                    type_scores[req_type] += 1
        
        # Return type with highest score, default to CONSTRAINT
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        else:
            return RequirementType.CONSTRAINT
    
    def _extract_entities(self, sentence: str) -> List[str]:
        """Extract named entities from the sentence"""
        entities = []
        
        if self.use_spacy and self.nlp:
            doc = self.nlp(sentence)
            entities.extend([ent.text.lower() for ent in doc.ents])
            # Also extract noun phrases
            entities.extend([chunk.text.lower() for chunk in doc.noun_chunks])
        else:
            # Simple entity extraction using patterns
            entity_patterns = [
                r'\b(system|user|application|service|database|server|client)\b',
                r'\b(number|integer|value|data|input|output|request|response)\b',
                r'\b([a-z]+(?:_[a-z]+)*)\b'  # Identifier-like words
            ]
            
            for pattern in entity_patterns:
                matches = re.findall(pattern, sentence.lower())
                entities.extend(matches)
        
        # Remove duplicates and filter
        entities = list(set(entities))
        return [e for e in entities if len(e) > 2]
    
    def _extract_predicates(self, sentence: str) -> List[str]:
        """Extract predicates (verbs and adjectives) from the sentence"""
        predicates = []
        
        if self.use_spacy and self.nlp:
            doc = self.nlp(sentence)
            predicates.extend([token.lemma_.lower() for token in doc if token.pos_ in ['VERB', 'ADJ']])
        else:
            # Simple predicate extraction using patterns
            predicate_patterns = [
                r'\b(is|are|was|were|be|been|being)\s+(\w+)',
                r'\b(must|shall|should|will|can|may)\s+(\w+)',
                r'\b(\w+)(?:ed|ing|s)?\b'  # Verb-like words
            ]
            
            for pattern in predicate_patterns:
                matches = re.findall(pattern, sentence.lower())
                for match in matches:
                    if isinstance(match, tuple):
                        predicates.extend(match)
                    else:
                        predicates.append(match)
        
        # Filter predicates
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        predicates = [p for p in predicates if p not in common_words and len(p) > 2]
        
        return list(set(predicates))
    
    def _analyze_logical_structure(self, sentence: str) -> LogicalStructure:
        """Analyze the logical structure of the sentence"""
        sentence_lower = sentence.lower()
        
        # Find quantifiers
        quantifiers = []
        for pattern in self.quantifier_patterns:
            matches = re.findall(pattern, sentence_lower)
            quantifiers.extend(matches)
        
        # Find conditionals
        conditionals = []
        for pattern in self.conditional_patterns:
            matches = re.findall(pattern, sentence_lower)
            conditionals.extend(matches)
        
        # Find logical operators
        logical_operators = []
        for pattern in self.logical_operator_patterns:
            matches = re.findall(pattern, sentence_lower)
            logical_operators.extend(matches)
        
        # Find temporal operators
        temporal_operators = []
        for pattern in self.temporal_patterns:
            matches = re.findall(pattern, sentence_lower)
            temporal_operators.extend(matches)
        
        return LogicalStructure(
            quantifiers=quantifiers,
            conditionals=conditionals,
            logical_operators=logical_operators,
            temporal_operators=temporal_operators,
            has_quantification=len(quantifiers) > 0,
            has_conditionals=len(conditionals) > 0,
            has_temporal=len(temporal_operators) > 0
        )
    
    def _extract_formal_constraints(self, sentence: str, entities: List[str], predicates: List[str]) -> List[FormalConstraint]:
        """Extract formal constraints that can be converted to Tau"""
        constraints = []
        
        # Pattern for mathematical relationships
        math_patterns = [
            (r'(\w+)\s+(?:is|equals?|=)\s+(\d+)', 'equality'),
            (r'(\w+)\s+(?:is\s+)?(?:greater\s+than?|>)\s+(\d+)', 'greater_than'),
            (r'(\w+)\s+(?:is\s+)?(?:less\s+than?|<)\s+(\d+)', 'less_than'),
            (r'(\w+)\s+(?:is\s+)?prime', 'prime'),
            (r'(\w+)\s+(?:is\s+)?even', 'even'),
            (r'(\w+)\s+(?:is\s+)?odd', 'odd')
        ]
        
        for pattern, constraint_type in math_patterns:
            matches = re.findall(pattern, sentence.lower())
            for match in matches:
                if isinstance(match, tuple):
                    var_name = match[0]
                    if len(match) > 1:
                        value = match[1]
                        logical_form = f"{constraint_type}({var_name}, {value})"
                    else:
                        logical_form = f"{constraint_type}({var_name})"
                else:
                    var_name = match
                    logical_form = f"{constraint_type}({var_name})"
                
                constraint = FormalConstraint(
                    constraint_type=constraint_type,
                    variables=[var_name],
                    predicates=[constraint_type],
                    logical_form=logical_form,
                    confidence=0.8
                )
                constraints.append(constraint)
        
        return constraints
    
    def _calculate_confidence(self, sentence: str, entities: List[str], predicates: List[str], logical_structure: LogicalStructure) -> float:
        """Calculate confidence score for requirement extraction"""
        score = 0.5  # Base score
        
        # Add points for clear structure
        if len(entities) > 0:
            score += 0.1
        if len(predicates) > 0:
            score += 0.1
        if logical_structure.has_quantification:
            score += 0.1
        if logical_structure.has_conditionals:
            score += 0.1
        
        # Add points for formal language
        formal_indicators = ['must', 'shall', 'should', 'required', 'specified']
        for indicator in formal_indicators:
            if indicator in sentence.lower():
                score += 0.05
        
        # Subtract points for ambiguous language
        ambiguous_words = ['properly', 'appropriately', 'suitable', 'adequate', 'reasonable']
        for word in ambiguous_words:
            if word in sentence.lower():
                score -= 0.1
        
        return max(0.0, min(1.0, score))
    
    def _categorize_from_section(self, section_title: str) -> str:
        """Categorize requirement based on section title"""
        title_lower = section_title.lower()
        
        category_keywords = {
            'validation': ['validation', 'input', 'verify'],
            'verification': ['verification', 'prime', 'check'],
            'output': ['output', 'display', 'return'],
            'performance': ['performance', 'time', 'speed'],
            'security': ['security', 'authentication', 'access'],
            'behavior': ['behavior', 'system', 'operation']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'general'


# Enhanced factory function
def create_requirements_analyzer() -> RequirementsAnalyzer:
    """Factory function to create a requirements analyzer"""
    return RequirementsAnalyzer()