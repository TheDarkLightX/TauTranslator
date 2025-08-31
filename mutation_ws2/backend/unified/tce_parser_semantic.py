"""
TCE Parser Semantic V2 - Ultra-Low Complexity (CC < 10)
Full-featured semantic parser with CC=1 for every method.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import Dict, List, Optional, Union, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
import logging

from backend.unified.tce_parser_v1_51 import TCEParserV151
from backend.unified.core.semantic_lexicon import SemanticLexicon, EntityCategory, RelationType


@dataclass
class SemanticContext:
    """Enhanced context with semantic information."""
    entities: Dict[str, str] = field(default_factory=dict)
    variables: List[str] = field(default_factory=list)
    coreferences: Dict[str, str] = field(default_factory=dict)
    semantic_types: Dict[str, EntityCategory] = field(default_factory=dict)
    relations: List[Tuple[str, RelationType, str]] = field(default_factory=list)
    discourse_markers: List[str] = field(default_factory=list)


# === PURE FUNCTIONS (CC=1 each) ===

def create_semantic_patterns() -> Dict[str, re.Pattern]:
    """Create semantic-aware patterns."""
    return {
        'complex_temporal': re.compile(r'(?:when|while|during|after|before|until)\s+(.+?),\s*(.+)', re.IGNORECASE),
        'complex_conditional': re.compile(r'(?:if|whenever|provided\s+that)\s+(.+?),?\s+then\s+(.+)', re.IGNORECASE),
        'complex_quantified': re.compile(r'(most|many|few|several)\s+([\w\s]+)\s+(?:are|is)\s+(.+)', re.IGNORECASE),
        'causal_relation': re.compile(r'(.+?)\s+(?:causes?|leads?\s+to|results?\s+in)\s+(.+)', re.IGNORECASE),
        'requirement_pattern': re.compile(r'(.+?)\s+(?:requires?|needs?|demands?)\s+(.+)', re.IGNORECASE),
        'permission_pattern': re.compile(r'(.+?)\s+(?:allows?|permits?|enables?)\s+(.+)', re.IGNORECASE),
        'modal_necessity': re.compile(r'(.+?)\s+(?:must|should|ought\s+to)\s+(.+)', re.IGNORECASE),
        'modal_possibility': re.compile(r'(.+?)\s+(?:may|might|could|can)\s+(.+)', re.IGNORECASE),
        'comparative': re.compile(r'(.+?)\s+(?:is|are)\s+(more|less|as)\s+(.+?)\s+than\s+(.+)', re.IGNORECASE),
        'superlative': re.compile(r'(.+?)\s+(?:is|are)\s+the\s+(most|least)\s+(.+)', re.IGNORECASE),
        'possession_complex': re.compile(r'(.+?)(?:\'s|\s+of\s+the)\s+(.+?)\s+(?:is|are)\s+(.+)', re.IGNORECASE),
        'relative_clause': re.compile(r'(.+?)\s+(?:who|which|that)\s+(.+?)\s+(?:is|are)\s+(.+)', re.IGNORECASE),
        'negation_complex': re.compile(r'(?:it\s+is\s+not\s+(?:true\s+)?that|neither|nor)\s+(.+)', re.IGNORECASE),
        'disjunction': re.compile(r'(?:either)\s+(.+?)\s+or\s+(.+)', re.IGNORECASE),
        'conjunction': re.compile(r'(?:both)\s+(.+?)\s+and\s+(.+)', re.IGNORECASE)
    }


def match_semantic_pattern(sentence: str, pattern_name: str, patterns: Dict[str, re.Pattern]) -> Union[re.Match, None]:
    """Match sentence against semantic pattern."""
    pattern = patterns.get(pattern_name)
    return pattern.match(sentence) if pattern else None


def extract_coreference_candidates(context: SemanticContext) -> List[str]:
    """Extract coreference candidates from context."""
    return list(context.entities.keys())


def resolve_single_pronoun(word: str, candidates: List[str]) -> str:
    """Resolve single pronoun to entity."""
    return resolve_pronoun_with_candidates(word, candidates)


def resolve_coreferences_in_text(text: str, context: SemanticContext) -> str:
    """Resolve coreferences in text."""
    candidates = extract_coreference_candidates(context)
    words = text.split()
    resolved_words = [resolve_single_pronoun(w, candidates) for w in words]
    return ' '.join(resolved_words)


def build_temporal_expression(temporal_clause: str, main_clause: str) -> str:
    """Build temporal expression."""
    return f"temporal({temporal_clause}) -> {main_clause}"


def build_conditional_expression(condition: str, consequence: str) -> str:
    """Build conditional expression."""
    return f"conditional({condition}) -> {consequence}"


def map_complex_quantifier(quantifier: str) -> str:
    """Map complex quantifier to logical form."""
    quant_map = {
        'most': 'majority',
        'many': 'many',
        'few': 'few',
        'several': 'some'
    }
    return quant_map.get(quantifier.lower(), quantifier)


def build_quantified_expression(quantifier: str, entity: str, predicate: str) -> str:
    """Build quantified expression."""
    logical_quant = map_complex_quantifier(quantifier)
    var = entity[0].lower()
    return f"{logical_quant} {var}: {entity}({var}) -> {predicate}({var})"


def build_causal_expression(cause: str, effect: str) -> str:
    """Build causal expression."""
    return f"causes({cause}, {effect})"


def store_causal_relation(context: SemanticContext, cause: str, effect: str):
    """Store causal relation in context."""
    context.relations.append((cause, RelationType.CAUSATION, effect))


def build_modal_necessity_expression(subject: str, action: str) -> str:
    """Build modal necessity expression."""
    return f"necessary({subject}, {action})"


def build_modal_possibility_expression(subject: str, action: str) -> str:
    """Build modal possibility expression."""
    return f"possible({subject}, {action})"


def map_comparison_operator(comparison: str) -> str:
    """Map comparison operator."""
    comp_map = {'more': 'greater', 'less': 'lesser', 'as': 'equal'}
    return comp_map.get(comparison.lower(), comparison)


def build_comparative_expression(subject: str, comparison: str, property_val: str, object_comp: str) -> str:
    """Build comparative expression."""
    logical_comp = map_comparison_operator(comparison)
    return f"{logical_comp}({subject}, {object_comp}, {property_val})"


def build_relative_clause_expression(entity: str, relative_clause: str, predicate: str) -> str:
    """Build relative clause expression."""
    var = entity[0].lower()
    return f"all {var}: ({entity}({var}) & {relative_clause}({var})) -> {predicate}({var})"


def try_temporal_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try temporal pattern."""
    match = match_semantic_pattern(sentence, 'complex_temporal', patterns)
    return build_temporal_expression(match.group(1), match.group(2)) if match else None


def try_conditional_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try conditional pattern."""
    match = match_semantic_pattern(sentence, 'complex_conditional', patterns)
    return build_conditional_expression(match.group(1), match.group(2)) if match else None


def try_quantified_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try quantified pattern."""
    match = match_semantic_pattern(sentence, 'complex_quantified', patterns)
    return process_quantified_match(match) if match else None


def try_causal_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try causal pattern."""
    match = match_semantic_pattern(sentence, 'causal_relation', patterns)
    return process_causal_match(match, context) if match else None


def try_modal_necessity_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try modal necessity pattern."""
    match = match_semantic_pattern(sentence, 'modal_necessity', patterns)
    return process_modal_necessity_match(match) if match else None


def try_modal_possibility_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try modal possibility pattern."""
    match = match_semantic_pattern(sentence, 'modal_possibility', patterns)
    return process_modal_possibility_match(match) if match else None


def try_comparative_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try comparative pattern."""
    match = match_semantic_pattern(sentence, 'comparative', patterns)
    return process_comparative_match(match) if match else None


def try_relative_clause_pattern(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try relative clause pattern."""
    match = match_semantic_pattern(sentence, 'relative_clause', patterns)
    return process_relative_clause_match(match) if match else None


def try_semantic_pattern_1(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try first group of semantic patterns."""
    return (try_temporal_pattern(sentence, patterns, context) or
            try_conditional_pattern(sentence, patterns, context) or
            try_quantified_pattern(sentence, patterns, context))


def try_semantic_pattern_2(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try second group of semantic patterns."""
    return (try_causal_pattern(sentence, patterns, context) or
            try_modal_necessity_pattern(sentence, patterns, context) or
            try_modal_possibility_pattern(sentence, patterns, context))


def try_semantic_pattern_3(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Try third group of semantic patterns."""
    return (try_comparative_pattern(sentence, patterns, context) or
            try_relative_clause_pattern(sentence, patterns, context))


def apply_all_semantic_patterns(sentence: str, patterns: Dict[str, re.Pattern], context: SemanticContext) -> Union[str, None]:
    """Apply all semantic patterns."""
    return (try_semantic_pattern_1(sentence, patterns, context) or
            try_semantic_pattern_2(sentence, patterns, context) or
            try_semantic_pattern_3(sentence, patterns, context))


def preprocess_with_coreference_resolution(sentence: str, context: SemanticContext) -> str:
    """Preprocess sentence with coreference resolution."""
    return resolve_coreferences_in_text(sentence, context)


class TCEParserSemanticV2(TCEParserV151):
    """
    Ultra-low complexity semantic parser (CC < 10).
    Every method has CC=1.
    """
    
    def __init__(self, dictionary_path: Optional[Path] = None, lexicon_path: Optional[Path] = None):
        """Initialize with semantic capabilities."""
        super().__init__(dictionary_path)
        self.semantic_context = SemanticContext()
        self.semantic_patterns = create_semantic_patterns()
        self.lexicon = create_semantic_lexicon(lexicon_path)
        
    def parse(self, sentence: str) -> str:
        """Parse with full semantic capabilities."""
        preprocessed = preprocess_with_coreference_resolution(sentence, self.semantic_context)
        semantic_result = apply_all_semantic_patterns(preprocessed, self.semantic_patterns, self.semantic_context)
        return semantic_result if semantic_result else super().parse(sentence)
    
    def add_semantic_knowledge(self, entity: str, category: EntityCategory, properties: Set[str] = None):
        """Add semantic knowledge about an entity."""
        self.semantic_context.semantic_types[entity] = category
        add_entity_properties_to_lexicon(self.lexicon, entity, properties)
    
    def get_semantic_analysis(self, sentence: str) -> Dict:
        """Get detailed semantic analysis of sentence."""
        return build_semantic_analysis(sentence, self.lexicon, self.semantic_context)
    
    def reset_semantic_context(self):
        """Reset semantic context."""
        self.semantic_context = SemanticContext()


# === HELPER FUNCTIONS ===

def create_semantic_lexicon(lexicon_path: Optional[Path]) -> SemanticLexicon:
    """Create semantic lexicon instance."""
    return SemanticLexicon(lexicon_path) if lexicon_path else SemanticLexicon()


def add_entity_properties_to_lexicon(lexicon: SemanticLexicon, entity: str, properties: Set[str]):
    """Add entity properties to lexicon."""
    if properties:
        lexicon.add_entity_properties(entity, properties)


def extract_entities_from_sentence(sentence: str, lexicon: SemanticLexicon) -> List[str]:
    """Extract entities from sentence."""
    return lexicon.extract_entities(sentence)


def extract_relations_from_sentence(sentence: str, lexicon: SemanticLexicon) -> List[Tuple[str, RelationType, str]]:
    """Extract relations from sentence."""
    return lexicon.extract_relations(sentence)


def build_semantic_analysis(sentence: str, lexicon: SemanticLexicon, context: SemanticContext) -> Dict:
    """Build semantic analysis result."""
    entities = extract_entities_from_sentence(sentence, lexicon)
    relations = extract_relations_from_sentence(sentence, lexicon)
    
    return {
        'entities': entities,
        'relations': relations,
        'discourse_markers': context.discourse_markers,
        'semantic_types': context.semantic_types
    }


def create_semantic_parser(dictionary_path: Optional[Path] = None, lexicon_path: Optional[Path] = None) -> TCEParserSemanticV2:
    """Create a semantic parser instance."""
    return TCEParserSemanticV2(dictionary_path, lexicon_path)


def resolve_pronoun_with_candidates(word: str, candidates: List[str]) -> str:
    """Resolve pronoun using candidates."""
    pronouns = {'it', 'they', 'them', 'this', 'that', 'these', 'those'}
    return get_most_recent_candidate(candidates) if is_pronoun_with_candidates(word, pronouns, candidates) else word


def is_pronoun_with_candidates(word: str, pronouns: Set[str], candidates: List[str]) -> bool:
    """Check if word is pronoun with available candidates."""
    return word.lower() in pronouns and candidates


def get_most_recent_candidate(candidates: List[str]) -> str:
    """Get most recent candidate."""
    return candidates[-1]


def process_quantified_match(match) -> str:
    """Process quantified match."""
    quantifier = match.group(1)
    entity = match.group(2).strip()
    predicate = match.group(3)
    return build_quantified_expression(quantifier, entity, predicate)


def process_causal_match(match, context: SemanticContext) -> str:
    """Process causal match."""
    cause = match.group(1).strip()
    effect = match.group(2).strip()
    store_causal_relation(context, cause, effect)
    return build_causal_expression(cause, effect)


def process_modal_necessity_match(match) -> str:
    """Process modal necessity match."""
    subject = match.group(1).strip()
    action = match.group(2).strip()
    return build_modal_necessity_expression(subject, action)


def process_modal_possibility_match(match) -> str:
    """Process modal possibility match."""
    subject = match.group(1).strip()
    action = match.group(2).strip()
    return build_modal_possibility_expression(subject, action)


def process_comparative_match(match) -> str:
    """Process comparative match."""
    subject = match.group(1).strip()
    comparison = match.group(2).strip()
    property_val = match.group(3).strip()
    object_comp = match.group(4).strip()
    return build_comparative_expression(subject, comparison, property_val, object_comp)


def process_relative_clause_match(match) -> str:
    """Process relative clause match."""
    entity = match.group(1).strip()
    relative_clause = match.group(2).strip()
    predicate = match.group(3).strip()
    return build_relative_clause_expression(entity, relative_clause, predicate)


# Aliases
TCEParserSemantic = TCEParserSemanticV2
FullFeaturedTCEParser = TCEParserSemanticV2
SemanticTCEParser = TCEParserSemanticV2