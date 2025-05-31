#!/usr/bin/env python3
"""
NLP Requirements Engine for TauTranslator
=========================================

Advanced NLP engine that converts natural language requirements
into formal Tau specifications through iterative refinement.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

# Try importing optional dependencies
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.chunk import ne_chunk
    from nltk.tag import pos_tag
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    # Fallback tokenization
    def sent_tokenize(text):
        return [s.strip() for s in text.split('.') if s.strip()]
    def word_tokenize(text):
        return text.split()
    def pos_tag(tokens):
        return [(t, 'NN') for t in tokens]

# Download required NLTK data
if NLTK_AVAILABLE:
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        nltk.download('maxent_ne_chunker', quiet=True)
        nltk.download('words', quiet=True)
    except:
        pass

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    """Types of requirements that can be extracted."""
    FUNCTIONAL = "functional"
    TEMPORAL = "temporal"
    CONSTRAINT = "constraint"
    INVARIANT = "invariant"
    STATE = "state"
    BEHAVIOR = "behavior"
    SAFETY = "safety"
    PERFORMANCE = "performance"


@dataclass
class ExtractedRequirement:
    """Represents an extracted requirement from natural language."""
    text: str
    type: RequirementType
    entities: Dict[str, List[str]] = field(default_factory=dict)
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    temporal_markers: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class TauSpecification:
    """Represents a Tau specification generated from requirements."""
    streams: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    invariants: List[str] = field(default_factory=list)
    temporal_properties: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class NLPRequirementsEngine:
    """
    Advanced NLP engine for requirements extraction and Tau generation.
    """
    
    def __init__(self, use_spacy: bool = True, use_transformers: bool = True):
        """Initialize the NLP engine with various models."""
        self.use_spacy = use_spacy
        self.use_transformers = use_transformers
        
        # Load spaCy model if available
        if use_spacy and SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except:
                logger.warning("spaCy model not available, install with: python -m spacy download en_core_web_sm")
                self.nlp = None
                self.use_spacy = False
        else:
            self.nlp = None
            self.use_spacy = False
        
        # Load transformer models if available
        if use_transformers and TRANSFORMERS_AVAILABLE:
            try:
                self.classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
                self.ner = pipeline("ner", aggregation_strategy="simple")
            except:
                logger.warning("Transformer models not available, using fallback")
                self.classifier = None
                self.ner = None
                self.use_transformers = False
        else:
            self.classifier = None
            self.ner = None
            self.use_transformers = False
        
        # Requirement patterns
        self.patterns = {
            'temporal': [
                r'\b(always|never|sometimes|eventually|until|whenever|when|after|before)\b',
                r'\b(at time|at any time|at all times|every time)\b',
                r'\b(within \d+ (seconds?|milliseconds?|minutes?))\b'
            ],
            'constraint': [
                r'\b(must|shall|should|cannot|must not|shall not)\b',
                r'\b(between|less than|greater than|equal to|at least|at most)\b',
                r'\b(maximum|minimum|limit|threshold|range)\b'
            ],
            'condition': [
                r'\b(if|when|unless|provided that|given that|in case)\b',
                r'\b(only if|if and only if|iff)\b'
            ],
            'action': [
                r'\b(calculate|compute|process|output|read|write|send|receive)\b',
                r'\b(check|verify|validate|ensure|maintain|monitor)\b',
                r'\b(start|stop|halt|pause|resume|reset)\b'
            ],
            'entity': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',  # Proper nouns
                r'\b(sensor|actuator|controller|system|module|component)\b',
                r'\b(input|output|signal|data|value|state|status)\b'
            ]
        }
        
    def extract_requirements(self, text: str) -> List[ExtractedRequirement]:
        """
        Extract structured requirements from natural language text.
        
        Args:
            text: Natural language requirements text
            
        Returns:
            List of extracted requirements
        """
        requirements = []
        
        # Split into sentences
        sentences = sent_tokenize(text) if text else []
        
        for sentence in sentences:
            req = self._extract_single_requirement(sentence)
            if req:
                requirements.append(req)
        
        return requirements
    
    def _extract_single_requirement(self, sentence: str) -> Optional[ExtractedRequirement]:
        """Extract requirement from a single sentence."""
        if not sentence.strip():
            return None
        
        req = ExtractedRequirement(text=sentence.strip(), type=RequirementType.FUNCTIONAL)
        
        # Classify requirement type
        req.type = self._classify_requirement_type(sentence)
        
        # Extract entities
        req.entities = self._extract_entities(sentence)
        
        # Extract temporal markers
        req.temporal_markers = self._extract_temporal_markers(sentence)
        
        # Extract conditions
        req.conditions = self._extract_conditions(sentence)
        
        # Extract actions
        req.actions = self._extract_actions(sentence)
        
        # Extract constraints
        req.constraints = self._extract_constraints(sentence)
        
        # Calculate confidence
        req.confidence = self._calculate_confidence(req)
        
        return req
    
    def _classify_requirement_type(self, sentence: str) -> RequirementType:
        """Classify the type of requirement."""
        sentence_lower = sentence.lower()
        
        # Use transformer classifier if available
        if self.classifier:
            labels = [t.value for t in RequirementType]
            result = self.classifier(sentence, candidate_labels=labels)
            return RequirementType(result['labels'][0])
        
        # Fallback to pattern matching
        if any(re.search(p, sentence_lower) for p in self.patterns['temporal']):
            if 'always' in sentence_lower or 'never' in sentence_lower:
                return RequirementType.INVARIANT
            return RequirementType.TEMPORAL
        
        if 'safety' in sentence_lower or 'emergency' in sentence_lower:
            return RequirementType.SAFETY
        
        if 'performance' in sentence_lower or 'within' in sentence_lower:
            return RequirementType.PERFORMANCE
        
        if any(word in sentence_lower for word in ['state', 'mode', 'status']):
            return RequirementType.STATE
        
        if any(re.search(p, sentence_lower) for p in self.patterns['constraint']):
            return RequirementType.CONSTRAINT
        
        return RequirementType.FUNCTIONAL
    
    def _extract_entities(self, sentence: str) -> Dict[str, List[str]]:
        """Extract named entities and domain objects."""
        entities = {
            'variables': [],
            'systems': [],
            'values': [],
            'files': []
        }
        
        # Use spaCy NER if available
        if self.nlp:
            doc = self.nlp(sentence)
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG']:
                    entities['systems'].append(ent.text)
                elif ent.label_ in ['CARDINAL', 'QUANTITY']:
                    entities['values'].append(ent.text)
        
        # Use transformer NER if available
        if self.ner:
            ner_results = self.ner(sentence)
            for result in ner_results:
                entities['variables'].append(result['word'])
        
        # Pattern-based extraction
        # Extract variable-like names
        var_pattern = r'\b([a-z_][a-z0-9_]*(?:_[a-z][a-z0-9_]*)*)\b'
        entities['variables'].extend(re.findall(var_pattern, sentence))
        
        # Extract file names
        file_pattern = r'"([^"]+\.[a-z]+)"'
        entities['files'].extend(re.findall(file_pattern, sentence))
        
        # Extract numeric values
        num_pattern = r'\b(\d+(?:\.\d+)?)\b'
        entities['values'].extend(re.findall(num_pattern, sentence))
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_temporal_markers(self, sentence: str) -> List[str]:
        """Extract temporal markers and time-related phrases."""
        markers = []
        
        for pattern in self.patterns['temporal']:
            matches = re.findall(pattern, sentence.lower())
            markers.extend(matches)
        
        return list(set(markers))
    
    def _extract_conditions(self, sentence: str) -> List[str]:
        """Extract conditional phrases."""
        conditions = []
        
        # Split by condition keywords
        for pattern in self.patterns['condition']:
            parts = re.split(pattern, sentence, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Get the condition part after the keyword
                conditions.append(parts[1].split(',')[0].strip())
        
        return conditions
    
    def _extract_actions(self, sentence: str) -> List[str]:
        """Extract action verbs and operations."""
        actions = []
        
        # Use POS tagging
        tokens = word_tokenize(sentence)
        pos_tags = pos_tag(tokens)
        
        # Extract verbs
        for token, pos in pos_tags:
            if pos.startswith('VB'):  # Verb
                actions.append(token.lower())
        
        # Pattern-based extraction
        for pattern in self.patterns['action']:
            matches = re.findall(pattern, sentence.lower())
            actions.extend(matches)
        
        return list(set(actions))
    
    def _extract_constraints(self, sentence: str) -> List[str]:
        """Extract constraints and bounds."""
        constraints = []
        
        # Numeric constraints
        constraint_patterns = [
            r'(between \d+ and \d+)',
            r'((?:less|greater) than(?: or equal to)? \d+)',
            r'(at (?:least|most) \d+)',
            r'(exactly \d+)',
            r'(\d+ to \d+)'
        ]
        
        for pattern in constraint_patterns:
            matches = re.findall(pattern, sentence.lower())
            constraints.extend(matches)
        
        return constraints
    
    def _calculate_confidence(self, req: ExtractedRequirement) -> float:
        """Calculate confidence score for the extracted requirement."""
        score = 0.5  # Base score
        
        # Boost for having entities
        if req.entities.get('variables'):
            score += 0.1
        
        # Boost for temporal markers
        if req.temporal_markers:
            score += 0.1
        
        # Boost for clear actions
        if req.actions:
            score += 0.1
        
        # Boost for constraints
        if req.constraints:
            score += 0.1
        
        # Boost for proper requirement type
        if req.type != RequirementType.FUNCTIONAL:
            score += 0.1
        
        return min(score, 1.0)
    
    def requirements_to_tau(self, requirements: List[ExtractedRequirement]) -> TauSpecification:
        """
        Convert extracted requirements to Tau specification.
        
        Args:
            requirements: List of extracted requirements
            
        Returns:
            TauSpecification object
        """
        spec = TauSpecification()
        
        # Process each requirement
        for req in requirements:
            if req.type == RequirementType.INVARIANT:
                tau_invariant = self._requirement_to_invariant(req)
                if tau_invariant:
                    spec.invariants.append(tau_invariant)
            
            elif req.type == RequirementType.TEMPORAL:
                tau_temporal = self._requirement_to_temporal(req)
                if tau_temporal:
                    spec.temporal_properties.append(tau_temporal)
            
            elif req.type in [RequirementType.FUNCTIONAL, RequirementType.BEHAVIOR]:
                tau_rule = self._requirement_to_rule(req)
                if tau_rule:
                    spec.rules.append(tau_rule)
            
            elif req.type == RequirementType.CONSTRAINT:
                tau_constraint = self._requirement_to_constraint(req)
                if tau_constraint:
                    spec.rules.append(tau_constraint)
            
            # Extract streams from entities
            for file in req.entities.get('files', []):
                if 'input' in req.text.lower():
                    spec.streams.append(f'sbf input_stream = ifile("{file}")')
                elif 'output' in req.text.lower():
                    spec.streams.append(f'sbf output_stream = ofile("{file}")')
        
        # Add metadata
        spec.metadata = {
            'num_requirements': len(requirements),
            'requirement_types': [req.type.value for req in requirements],
            'average_confidence': sum(req.confidence for req in requirements) / len(requirements) if requirements else 0
        }
        
        return spec
    
    def _requirement_to_invariant(self, req: ExtractedRequirement) -> Optional[str]:
        """Convert invariant requirement to Tau always/never statement."""
        if 'always' in req.temporal_markers:
            # Build the condition
            condition = self._build_tau_expression(req)
            if condition:
                return f"always {condition}"
        
        elif 'never' in req.temporal_markers:
            condition = self._build_tau_expression(req)
            if condition:
                return f"always ~({condition})"
        
        return None
    
    def _requirement_to_temporal(self, req: ExtractedRequirement) -> Optional[str]:
        """Convert temporal requirement to Tau temporal property."""
        if 'sometimes' in req.temporal_markers or 'eventually' in req.temporal_markers:
            condition = self._build_tau_expression(req)
            if condition:
                return f"sometimes {condition}"
        
        return None
    
    def _requirement_to_rule(self, req: ExtractedRequirement) -> Optional[str]:
        """Convert functional requirement to Tau rule."""
        # Extract the main variable
        variables = req.entities.get('variables', [])
        if not variables:
            return None
        
        main_var = variables[0]
        
        # Build the rule expression
        expression = self._build_tau_expression(req)
        
        if expression:
            return f"r {main_var}[t] = {expression}"
        
        return None
    
    def _requirement_to_constraint(self, req: ExtractedRequirement) -> Optional[str]:
        """Convert constraint requirement to Tau rule or invariant."""
        if req.constraints:
            # Parse numeric constraints
            for constraint in req.constraints:
                if 'between' in constraint:
                    match = re.search(r'between (\d+) and (\d+)', constraint)
                    if match:
                        min_val, max_val = match.groups()
                        var = req.entities.get('variables', ['value'])[0]
                        return f"always {var}[t] >= {min_val} & {var}[t] <= {max_val}"
        
        return None
    
    def _build_tau_expression(self, req: ExtractedRequirement) -> Optional[str]:
        """Build a Tau expression from requirement components."""
        parts = []
        
        # Handle conditions
        if req.conditions:
            # Simple condition mapping
            condition = req.conditions[0]
            # Try to extract variable comparisons
            if 'greater than' in condition:
                match = re.search(r'(\w+).*greater than (\d+)', condition)
                if match:
                    var, val = match.groups()
                    parts.append(f"{var}[t] > {val}")
        
        # Handle actions
        if 'calculate' in req.actions and 'average' in req.text.lower():
            # Moving average pattern
            var = req.entities.get('variables', ['input'])[0]
            parts.append(f"({var}[t] + {var}[t-1] + {var}[t-2]) / 3")
        
        # Default to simple variable reference
        if not parts and req.entities.get('variables'):
            parts.append(f"{req.entities['variables'][0]}[t]")
        
        return ' & '.join(parts) if parts else None
    
    def generate_tau_code(self, spec: TauSpecification) -> str:
        """Generate formatted Tau code from specification."""
        lines = []
        
        # Add header comment
        lines.append("# Generated Tau Specification")
        lines.append("# " + "=" * 40)
        lines.append("")
        
        # Add streams
        if spec.streams:
            lines.append("# Stream Declarations")
            lines.extend(spec.streams)
            lines.append("")
        
        # Add functions
        if spec.functions:
            lines.append("# Function Definitions")
            lines.extend(spec.functions)
            lines.append("")
        
        # Add rules
        if spec.rules:
            lines.append("# Rules")
            lines.extend(spec.rules)
            lines.append("")
        
        # Add invariants
        if spec.invariants:
            lines.append("# Invariants")
            lines.extend(spec.invariants)
            lines.append("")
        
        # Add temporal properties
        if spec.temporal_properties:
            lines.append("# Temporal Properties")
            lines.extend(spec.temporal_properties)
            lines.append("")
        
        return '\n'.join(lines)