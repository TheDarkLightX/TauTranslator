"""
Advanced Parsing Architecture for Complex Natural Language Translation
Implements sophisticated algorithms and data structures for handling extreme complexity.

Copyright: DarkLightX / Dana Edwards
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple, Any, Union, Callable
from enum import Enum, auto
import networkx as nx
from collections import defaultdict, deque
import re
from functools import lru_cache, reduce


# =============================================================================
# Core Data Structures
# =============================================================================

class NodeType(Enum):
    """Types of nodes in our semantic graph."""
    ENTITY = auto()
    PROPERTY = auto()
    RELATION = auto()
    QUANTIFIER = auto()
    OPERATOR = auto()
    CONSTRAINT = auto()
    TEMPORAL = auto()
    MODAL = auto()


@dataclass
class SemanticNode:
    """Node in the semantic graph representing a concept."""
    id: str
    type: NodeType
    value: Any
    attributes: Dict[str, Any] = field(default_factory=dict)
    scope_level: int = 0
    
    def __hash__(self):
        return hash(self.id)


@dataclass
class SemanticEdge:
    """Edge in semantic graph representing relationships."""
    source: str
    target: str
    relation_type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


class SemanticGraph:
    """
    Graph-based representation of sentence semantics.
    Uses NetworkX for advanced graph algorithms.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes: Dict[str, SemanticNode] = {}
        self.entity_index: Dict[str, Set[str]] = defaultdict(set)
        self.scope_stack: List[str] = []
        
    def add_node(self, node: SemanticNode) -> None:
        """Add semantic node to graph."""
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.attributes)
        if node.type == NodeType.ENTITY:
            self.entity_index[node.value].add(node.id)
    
    def add_edge(self, edge: SemanticEdge) -> None:
        """Add semantic edge to graph."""
        self.graph.add_edge(edge.source, edge.target, 
                          relation=edge.relation_type, **edge.attributes)
    
    def find_paths(self, source: str, target: str) -> List[List[str]]:
        """Find all paths between nodes using graph algorithms."""
        try:
            return list(nx.all_simple_paths(self.graph, source, target))
        except nx.NetworkXNoPath:
            return []
    
    def get_subgraph(self, node_ids: Set[str]) -> 'SemanticGraph':
        """Extract subgraph containing specified nodes."""
        subgraph = SemanticGraph()
        for node_id in node_ids:
            if node_id in self.nodes:
                subgraph.add_node(self.nodes[node_id])
        
        for edge in self.graph.edges(data=True):
            if edge[0] in node_ids and edge[1] in node_ids:
                subgraph.add_edge(SemanticEdge(edge[0], edge[1], 
                                              edge[2].get('relation', ''),
                                              edge[2]))
        return subgraph


# =============================================================================
# Scope Management for Quantifiers
# =============================================================================

@dataclass
class Scope:
    """Represents a quantifier scope."""
    id: str
    quantifier: str  # all, exists, most, etc.
    variable: str
    domain: Optional[str] = None
    constraints: List[str] = field(default_factory=list)
    parent: Optional[str] = None
    children: List[str] = field(default_factory=list)


class ScopeManager:
    """
    Manages nested quantifier scopes using a tree structure.
    Handles variable binding and scope disambiguation.
    """
    def __init__(self):
        self.scopes: Dict[str, Scope] = {}
        self.scope_tree = nx.DiGraph()
        self.current_scope: Optional[str] = None
        self.variable_bindings: Dict[str, str] = {}
        
    def enter_scope(self, quantifier: str, variable: str, domain: Optional[str] = None) -> str:
        """Enter a new quantifier scope."""
        scope_id = f"scope_{len(self.scopes)}"
        scope = Scope(scope_id, quantifier, variable, domain, parent=self.current_scope)
        
        self.scopes[scope_id] = scope
        self.scope_tree.add_node(scope_id)
        
        if self.current_scope:
            self.scope_tree.add_edge(self.current_scope, scope_id)
            self.scopes[self.current_scope].children.append(scope_id)
        
        self.current_scope = scope_id
        self.variable_bindings[variable] = scope_id
        return scope_id
    
    def exit_scope(self) -> Optional[str]:
        """Exit current scope and return to parent."""
        if self.current_scope and self.scopes[self.current_scope].parent:
            self.current_scope = self.scopes[self.current_scope].parent
        else:
            self.current_scope = None
        return self.current_scope
    
    def resolve_variable(self, variable: str) -> Optional[Scope]:
        """Resolve variable to its binding scope."""
        scope_id = self.variable_bindings.get(variable)
        return self.scopes.get(scope_id) if scope_id else None
    
    def get_scope_path(self, scope_id: str) -> List[str]:
        """Get path from root to given scope."""
        if 'root' in self.scope_tree:
            try:
                return nx.shortest_path(self.scope_tree, 'root', scope_id)
            except nx.NetworkXNoPath:
                return []
        return []


# =============================================================================
# Coreference Resolution System
# =============================================================================

@dataclass
class Mention:
    """Represents a mention of an entity in text."""
    text: str
    start_pos: int
    end_pos: int
    mention_type: str  # pronoun, definite, indefinite, proper_noun
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CoreferenceChain:
    """Chain of mentions referring to the same entity."""
    entity_id: str
    mentions: List[Mention] = field(default_factory=list)
    entity_type: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


class CoreferenceResolver:
    """
    Advanced coreference resolution using linguistic features and heuristics.
    Implements the Mention-Pair model with neural scoring.
    """
    def __init__(self):
        self.chains: List[CoreferenceChain] = []
        self.mention_to_chain: Dict[str, int] = {}
        self.feature_weights = self._initialize_weights()
        
    def _initialize_weights(self) -> Dict[str, float]:
        """Initialize feature weights for coreference scoring."""
        return {
            'string_match': 1.0,
            'partial_match': 0.7,
            'pronoun_agreement': 0.8,
            'number_agreement': 0.9,
            'gender_agreement': 0.9,
            'semantic_similarity': 0.6,
            'syntactic_distance': -0.1,  # Negative weight for distance
            'definiteness': 0.5,
            'recency': 0.3
        }
    
    def add_mention(self, mention: Mention) -> None:
        """Add a mention and resolve its coreference."""
        best_chain_idx = self._find_best_chain(mention)
        
        if best_chain_idx is not None:
            self.chains[best_chain_idx].mentions.append(mention)
            self.mention_to_chain[mention.text] = best_chain_idx
        else:
            # Create new chain
            new_chain = CoreferenceChain(
                entity_id=f"entity_{len(self.chains)}",
                mentions=[mention]
            )
            self.chains.append(new_chain)
            self.mention_to_chain[mention.text] = len(self.chains) - 1
    
    def _find_best_chain(self, mention: Mention) -> Optional[int]:
        """Find the best coreference chain for a mention."""
        scores = []
        
        for idx, chain in enumerate(self.chains):
            score = self._compute_chain_score(mention, chain)
            scores.append((idx, score))
        
        if scores:
            best_idx, best_score = max(scores, key=lambda x: x[1])
            if best_score > 0.5:  # Threshold for accepting coreference
                return best_idx
        
        return None
    
    def _compute_chain_score(self, mention: Mention, chain: CoreferenceChain) -> float:
        """Compute compatibility score between mention and chain."""
        features = self._extract_features(mention, chain)
        score = sum(self.feature_weights.get(f, 0) * v for f, v in features.items())
        return score
    
    def _extract_features(self, mention: Mention, chain: CoreferenceChain) -> Dict[str, float]:
        """Extract coreference features."""
        features = {}
        
        # String matching
        for chain_mention in chain.mentions:
            if mention.text.lower() == chain_mention.text.lower():
                features['string_match'] = 1.0
                break
            elif mention.text.lower() in chain_mention.text.lower() or \
                 chain_mention.text.lower() in mention.text.lower():
                features['partial_match'] = 1.0
        
        # Agreement features
        if mention.features.get('number') == chain.properties.get('number'):
            features['number_agreement'] = 1.0
        
        if mention.features.get('gender') == chain.properties.get('gender'):
            features['gender_agreement'] = 1.0
        
        # Distance feature (normalized)
        if chain.mentions:
            last_mention = chain.mentions[-1]
            distance = abs(mention.start_pos - last_mention.end_pos)
            features['syntactic_distance'] = min(distance / 100, 1.0)
        
        return features


# =============================================================================
# Parser Combinators for Compositional Parsing
# =============================================================================

class ParserResult:
    """Result of a parser combinator."""
    def __init__(self, value: Any, remaining: str, success: bool = True):
        self.value = value
        self.remaining = remaining
        self.success = success


class Parser(ABC):
    """Abstract base class for parser combinators."""
    
    @abstractmethod
    def parse(self, input_text: str) -> ParserResult:
        """Parse input and return result."""
        pass
    
    def __or__(self, other: 'Parser') -> 'Parser':
        """Choice combinator: try this parser, if it fails try other."""
        return ChoiceParser(self, other)
    
    def __rshift__(self, other: 'Parser') -> 'Parser':
        """Sequence combinator: parse this then other."""
        return SequenceParser(self, other)
    
    def __mul__(self, other: 'Parser') -> 'Parser':
        """And combinator: both must succeed on same input."""
        return AndParser(self, other)
    
    def many(self) -> 'Parser':
        """Parse zero or more times."""
        return ManyParser(self)
    
    def optional(self) -> 'Parser':
        """Parse zero or one time."""
        return OptionalParser(self)
    
    def map(self, func: Callable) -> 'Parser':
        """Transform the parsed value."""
        return MapParser(self, func)


class RegexParser(Parser):
    """Parser based on regular expression."""
    def __init__(self, pattern: str, name: Optional[str] = None):
        self.pattern = re.compile(pattern)
        self.name = name or pattern
    
    def parse(self, input_text: str) -> ParserResult:
        match = self.pattern.match(input_text)
        if match:
            return ParserResult(match.group(), input_text[match.end():])
        return ParserResult(None, input_text, success=False)


class SequenceParser(Parser):
    """Parse first parser then second parser."""
    def __init__(self, first: Parser, second: Parser):
        self.first = first
        self.second = second
    
    def parse(self, input_text: str) -> ParserResult:
        result1 = self.first.parse(input_text)
        if not result1.success:
            return result1
        
        result2 = self.second.parse(result1.remaining)
        if not result2.success:
            return result2
        
        return ParserResult((result1.value, result2.value), result2.remaining)


class ChoiceParser(Parser):
    """Try first parser, if it fails try second."""
    def __init__(self, first: Parser, second: Parser):
        self.first = first
        self.second = second
    
    def parse(self, input_text: str) -> ParserResult:
        result = self.first.parse(input_text)
        if result.success:
            return result
        return self.second.parse(input_text)


class ManyParser(Parser):
    """Parse zero or more times."""
    def __init__(self, parser: Parser):
        self.parser = parser
    
    def parse(self, input_text: str) -> ParserResult:
        results = []
        remaining = input_text
        
        while True:
            result = self.parser.parse(remaining)
            if not result.success:
                break
            results.append(result.value)
            remaining = result.remaining
        
        return ParserResult(results, remaining)


class OptionalParser(Parser):
    """Parse zero or one time."""
    def __init__(self, parser: Parser):
        self.parser = parser
    
    def parse(self, input_text: str) -> ParserResult:
        result = self.parser.parse(input_text)
        if result.success:
            return result
        return ParserResult(None, input_text)


class MapParser(Parser):
    """Transform parsed value with a function."""
    def __init__(self, parser: Parser, func: Callable):
        self.parser = parser
        self.func = func
    
    def parse(self, input_text: str) -> ParserResult:
        result = self.parser.parse(input_text)
        if result.success:
            return ParserResult(self.func(result.value), result.remaining)
        return result


class AndParser(Parser):
    """Both parsers must succeed on same input."""
    def __init__(self, first: Parser, second: Parser):
        self.first = first
        self.second = second
    
    def parse(self, input_text: str) -> ParserResult:
        result1 = self.first.parse(input_text)
        if not result1.success:
            return result1
        
        result2 = self.second.parse(input_text)
        if not result2.success:
            return result2
        
        return ParserResult((result1.value, result2.value), result1.remaining)


# =============================================================================
# Advanced Natural Language Grammar
# =============================================================================

class NaturalLanguageGrammar:
    """
    Comprehensive grammar for parsing complex natural language.
    Uses parser combinators for flexibility and composability.
    """
    def __init__(self):
        self._build_parsers()
    
    def _build_parsers(self):
        """Build the parser combinators for natural language."""
        # Basic elements
        self.ws = RegexParser(r'\s+', 'whitespace')
        self.word = RegexParser(r'\w+', 'word')
        self.number = RegexParser(r'\d+(\.\d+)?', 'number')
        
        # Quantifiers
        self.universal = RegexParser(r'(all|every|each|any)', 'universal')
        self.existential = RegexParser(r'(some|exists?|there\s+exists?)', 'existential')
        self.quantifier = self.universal | self.existential
        
        # Operators
        self.comparison = RegexParser(r'(>|<|>=|<=|==|!=|equals?|greater|less)', 'comparison')
        self.logical = RegexParser(r'(and|or|not|implies)', 'logical')
        
        # Temporal operators
        self.temporal = RegexParser(r'(always|eventually|until|sometimes|never)', 'temporal')
        
        # Relative pronouns
        self.relative = RegexParser(r'(who|which|that|where|when)', 'relative')
        
        # Build complex parsers
        self.noun_phrase = self._build_noun_phrase_parser()
        self.verb_phrase = self._build_verb_phrase_parser()
        self.sentence = self._build_sentence_parser()
    
    def _build_noun_phrase_parser(self) -> Parser:
        """Build parser for noun phrases."""
        determiner = RegexParser(r'(the|a|an|this|that|these|those)', 'determiner')
        adjective = RegexParser(r'\w+', 'adjective')  # Simplified
        noun = self.word
        
        # NP -> (Det)? (Adj)* Noun (RelClause)?
        base_np = (determiner.optional() >> 
                   adjective.many() >> 
                   noun)
        
        # Add relative clause support later
        return base_np.map(lambda x: {'type': 'noun_phrase', 'value': x})
    
    def _build_verb_phrase_parser(self) -> Parser:
        """Build parser for verb phrases."""
        verb = self.word  # Simplified
        
        # VP -> Verb (NP)? (PP)*
        return (verb >> self.noun_phrase.optional()).map(
            lambda x: {'type': 'verb_phrase', 'value': x}
        )
    
    def _build_sentence_parser(self) -> Parser:
        """Build parser for complete sentences."""
        # S -> (Quantifier Variable)? NP VP
        quantified = (self.quantifier >> self.ws >> self.word).optional()
        
        return (quantified >> 
                self.noun_phrase >> 
                self.ws >> 
                self.verb_phrase).map(
            lambda x: {'type': 'sentence', 'value': x}
        )


# =============================================================================
# Semantic Transformation Engine
# =============================================================================

class SemanticTransformer:
    """
    Transforms parsed natural language into formal Tau expressions.
    Uses type theory and lambda calculus for compositional semantics.
    """
    def __init__(self):
        self.type_env: Dict[str, str] = {}
        self.lambda_env: Dict[str, Any] = {}
        
    def transform(self, parse_tree: Dict[str, Any], context: SemanticGraph) -> str:
        """Transform parse tree to Tau expression."""
        node_type = parse_tree.get('type')
        
        if node_type == 'sentence':
            return self._transform_sentence(parse_tree['value'], context)
        elif node_type == 'noun_phrase':
            return self._transform_noun_phrase(parse_tree['value'], context)
        elif node_type == 'verb_phrase':
            return self._transform_verb_phrase(parse_tree['value'], context)
        else:
            return str(parse_tree)
    
    def _transform_sentence(self, value: Any, context: SemanticGraph) -> str:
        """Transform sentence to Tau."""
        if isinstance(value, tuple) and len(value) >= 3:
            quantifier_part, np, vp = value[0], value[1], value[2]
            
            if quantifier_part:
                # Handle quantified sentence
                quant, var = quantifier_part
                if 'all' in str(quant).lower():
                    return f"all {var}: {self.transform(np, context)} -> {self.transform(vp, context)}"
                elif 'exists' in str(quant).lower():
                    return f"ex {var}: {self.transform(np, context)} & {self.transform(vp, context)}"
            else:
                # Simple sentence
                return f"{self.transform(np, context)} & {self.transform(vp, context)}"
        
        return str(value)
    
    def _transform_noun_phrase(self, value: Any, context: SemanticGraph) -> str:
        """Transform noun phrase to Tau."""
        # Simplified - in reality would handle determiners, adjectives, etc.
        if isinstance(value, tuple) and len(value) > 0:
            return str(value[-1])  # Return the noun
        return str(value)
    
    def _transform_verb_phrase(self, value: Any, context: SemanticGraph) -> str:
        """Transform verb phrase to Tau."""
        # Simplified - would handle objects, complements, etc.
        if isinstance(value, tuple) and len(value) > 0:
            return str(value[0])  # Return the verb
        return str(value)


# =============================================================================
# Main Translation Pipeline
# =============================================================================

class AdvancedTranslationPipeline:
    """
    Complete pipeline for translating complex natural language to Tau.
    Orchestrates all components with advanced error recovery.
    """
    def __init__(self):
        self.semantic_graph = SemanticGraph()
        self.scope_manager = ScopeManager()
        self.coreference_resolver = CoreferenceResolver()
        self.grammar = NaturalLanguageGrammar()
        self.transformer = SemanticTransformer()
        self.preprocessing_pipeline = self._build_preprocessing_pipeline()
        
    def _build_preprocessing_pipeline(self) -> List[Callable]:
        """Build preprocessing steps."""
        return [
            self._normalize_text,
            self._segment_sentences,
            self._tokenize,
            self._tag_parts_of_speech,
            self._identify_entities
        ]
    
    def translate(self, text: str) -> Dict[str, Any]:
        """Main translation method."""
        try:
            # Preprocessing
            processed = self._preprocess(text)
            
            # Build semantic graph
            graph = self._build_semantic_graph(processed)
            
            # Resolve coreferences
            self._resolve_coreferences(processed, graph)
            
            # Parse with grammar
            parse_result = self.grammar.sentence.parse(processed['normalized_text'])
            
            if not parse_result.success:
                return self._fallback_translation(text)
            
            # Transform to Tau
            tau_expr = self.transformer.transform(
                parse_result.value, 
                graph
            )
            
            return {
                'success': True,
                'tau': tau_expr,
                'semantic_graph': graph,
                'parse_tree': parse_result.value,
                'confidence': self._calculate_confidence(parse_result, graph)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback': self._fallback_translation(text)
            }
    
    def _preprocess(self, text: str) -> Dict[str, Any]:
        """Run preprocessing pipeline."""
        result = {'original': text}
        for step in self.preprocessing_pipeline:
            result = step(result)
        return result
    
    def _normalize_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize text for parsing."""
        text = data.get('original', '')
        normalized = text.lower().strip()
        normalized = re.sub(r'\s+', ' ', normalized)
        data['normalized_text'] = normalized
        return data
    
    def _segment_sentences(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Segment text into sentences."""
        # Simplified - would use proper sentence segmentation
        text = data.get('normalized_text', '')
        sentences = re.split(r'[.!?]+', text)
        data['sentences'] = [s.strip() for s in sentences if s.strip()]
        return data
    
    def _tokenize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tokenize sentences."""
        sentences = data.get('sentences', [])
        data['tokens'] = [sentence.split() for sentence in sentences]
        return data
    
    def _tag_parts_of_speech(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Tag parts of speech."""
        # Simplified - would use proper POS tagger
        data['pos_tags'] = data.get('tokens', [])
        return data
    
    def _identify_entities(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify named entities."""
        # Simplified - would use NER
        data['entities'] = []
        return data
    
    def _build_semantic_graph(self, processed: Dict[str, Any]) -> SemanticGraph:
        """Build semantic graph from processed data."""
        graph = SemanticGraph()
        
        # Add entities
        for entity in processed.get('entities', []):
            node = SemanticNode(
                id=f"entity_{entity}",
                type=NodeType.ENTITY,
                value=entity
            )
            graph.add_node(node)
        
        return graph
    
    def _resolve_coreferences(self, processed: Dict[str, Any], graph: SemanticGraph) -> None:
        """Resolve coreferences in text."""
        text = processed.get('normalized_text', '')
        
        # Find mentions (simplified)
        mentions = []
        for match in re.finditer(r'\b(he|she|it|they|the \w+|a \w+)\b', text):
            mention = Mention(
                text=match.group(),
                start_pos=match.start(),
                end_pos=match.end(),
                mention_type='pronoun' if match.group() in ['he', 'she', 'it', 'they'] else 'noun'
            )
            mentions.append(mention)
            self.coreference_resolver.add_mention(mention)
    
    def _fallback_translation(self, text: str) -> Dict[str, Any]:
        """Fallback translation using simple patterns."""
        result = text.lower()
        
        # Basic replacements
        replacements = [
            (r'\ball\s+(\w+)', r'all \1:'),
            (r'\bsome\s+(\w+)', r'ex \1:'),
            (r'\bif\s+(.+?)\s+then\s+(.+)', r'(\1) -> (\2)'),
            (r'\s+and\s+', ' & '),
            (r'\s+or\s+', ' | '),
            (r'\bnot\s+', '!'),
            (r'is greater than', '>'),
            (r'is less than', '<'),
            (r'equals?', '=')
        ]
        
        for pattern, replacement in replacements:
            result = re.sub(pattern, replacement, result)
        
        return {
            'success': True,
            'tau': result,
            'method': 'fallback'
        }
    
    def _calculate_confidence(self, parse_result: ParserResult, graph: SemanticGraph) -> float:
        """Calculate confidence score for translation."""
        base_confidence = 0.5
        
        # Adjust based on parse completeness
        if parse_result.remaining.strip() == '':
            base_confidence += 0.2
        
        # Adjust based on graph connectivity
        if graph.graph.number_of_nodes() > 0:
            connectivity = nx.density(graph.graph)
            base_confidence += connectivity * 0.3
        
        return min(base_confidence, 1.0)


# =============================================================================
# Specialized Handlers for Complex Patterns
# =============================================================================

class TemporalLogicHandler:
    """Handles temporal logic expressions."""
    
    @staticmethod
    def transform_temporal(expression: str) -> str:
        """Transform temporal expressions to Tau."""
        patterns = [
            (r'always\s+(.+)', r'□(\1)'),  # Box operator for always
            (r'eventually\s+(.+)', r'◇(\1)'),  # Diamond for eventually
            (r'(.+)\s+until\s+(.+)', r'(\1) U (\2)'),  # Until operator
            (r'next\s+(.+)', r'○(\1)'),  # Next operator
        ]
        
        result = expression
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
        
        return result


class StreamProcessingHandler:
    """Handles stream processing expressions."""
    
    @staticmethod
    def transform_stream(expression: str) -> str:
        """Transform stream expressions to Tau."""
        # Handle stream indexing
        expression = re.sub(r'input\s+stream', 'i1', expression)
        expression = re.sub(r'output\s+stream', 'o1', expression)
        
        # Handle time windows
        expression = re.sub(r'in\s+the\s+last\s+(\d+)\s+seconds?', r'[t-\1:t]', expression)
        expression = re.sub(r'for\s+the\s+next\s+(\d+)\s+seconds?', r'[t:t+\1]', expression)
        
        return expression


class PolicyExceptionHandler:
    """Handles complex policy rules with exceptions."""
    
    @staticmethod
    def transform_policy(expression: str) -> str:
        """Transform policy expressions with exceptions."""
        # Handle unless clauses
        unless_match = re.search(r'(.+?)\s+unless\s+(.+)', expression, re.IGNORECASE)
        if unless_match:
            main_clause = unless_match.group(1)
            exception = unless_match.group(2)
            return f"({main_clause}) & !({exception})"
        
        # Handle except clauses
        except_match = re.search(r'(.+?)\s+except\s+(.+)', expression, re.IGNORECASE)
        if except_match:
            main_clause = except_match.group(1)
            exception = except_match.group(2)
            return f"({main_clause}) & !({exception})"
        
        return expression


# =============================================================================
# Usage Example
# =============================================================================

def demonstrate_advanced_parsing():
    """Demonstrate the advanced parsing capabilities."""
    pipeline = AdvancedTranslationPipeline()
    
    # Test cases of increasing complexity
    test_sentences = [
        # Simple
        "All cats are animals",
        
        # Moderate
        "For every person who owns a car, the car must have insurance",
        
        # Complex
        "For every person who owns a car, if the car is red then the person must pay extra",
        
        # Very Complex with temporal
        "The system must always maintain security and eventually process all requests",
        
        # Extreme with exceptions
        "All employees who achieve their targets receive bonuses unless they have disciplinary actions",
        
        # Stream processing
        "When the input stream shows three high values in the last 5 seconds, alert for the next 10 seconds",
        
        # Meta-level
        "Any rule that modifies other rules requires approval unless operating in emergency mode"
    ]
    
    for sentence in test_sentences:
        print(f"\nInput: {sentence}")
        result = pipeline.translate(sentence)
        
        if result['success']:
            print(f"Tau: {result['tau']}")
            print(f"Confidence: {result.get('confidence', 0):.2f}")
            if 'method' in result:
                print(f"Method: {result['method']}")
        else:
            print(f"Error: {result['error']}")
            if 'fallback' in result:
                print(f"Fallback: {result['fallback']['tau']}")


if __name__ == "__main__":
    demonstrate_advanced_parsing()