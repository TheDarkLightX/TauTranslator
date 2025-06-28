#!/usr/bin/env python3
"""
Abstract Meaning Representation (AMR) Semantic Layer
==================================================

Enhanced NLP capabilities for TauTranslator using state-of-the-art AMR techniques.
Provides deep semantic understanding for Tau Controlled English (TCE).

Based on research from:
- MASSIVE-AMR 2024 multilingual dataset
- Neuro-symbolic AMR parsing
- Compositional semantics for formal languages
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum, auto
import re

from ...parsers.cnl_parser.ast_nodes import ASTNode, PredicateCallNode, VariableNode, QuantifierBlockNode


class AMRRelation(Enum):
    """Standard AMR semantic relations"""
    ARG0 = "ARG0"  # Agent/subject
    ARG1 = "ARG1"  # Patient/object
    ARG2 = "ARG2"  # Beneficiary/indirect object
    ARG3 = "ARG3"  # Starting point
    ARG4 = "ARG4"  # Ending point
    
    # Modifier relations
    TEMPORAL = "temporal"
    LOCATION = "location"
    MANNER = "manner"
    PURPOSE = "purpose"
    CONDITION = "condition"
    
    # Quantifier relations
    QUANT = "quant"
    SCOPE = "scope"
    DOMAIN = "domain"
    
    # Predicate relations
    POLARITY = "polarity"
    MODE = "mode"


@dataclass
class AMRConcept:
    """
    Represents an AMR concept with its frame semantics.
    Maps TCE predicates to semantic frames.
    """
    name: str
    frame_type: str  # predicate, entity, operator, quantifier
    roles: List[AMRRelation]
    constraints: Dict[str, Any]
    
    def __post_init__(self):
        if not self.constraints:
            self.constraints = {}


@dataclass 
class AMRInstance:
    """
    An instance of an AMR concept in a specific context.
    """
    concept: AMRConcept
    instance_id: str
    arguments: Dict[AMRRelation, 'AMRInstance']
    
    def __post_init__(self):
        if not self.arguments:
            self.arguments = {}


class AMRGraph:
    """
    Represents the complete AMR graph for a TCE sentence.
    
    Provides semantic role labeling, coreference resolution,
    and compositional meaning representation.
    """
    
    def __init__(self):
        self.instances: Dict[str, AMRInstance] = {}
        self.root: Optional[str] = None
        self.edges: List[Tuple[str, AMRRelation, str]] = []
        self.variables: Set[str] = set()
        
    def add_instance(self, instance_id: str, concept: AMRConcept) -> AMRInstance:
        """Add a new concept instance to the graph"""
        instance = AMRInstance(concept, instance_id, {})
        self.instances[instance_id] = instance
        return instance
    
    def add_edge(self, source_id: str, relation: AMRRelation, target_id: str):
        """Add a semantic relation between instances"""
        if source_id in self.instances and target_id in self.instances:
            self.edges.append((source_id, relation, target_id))
            self.instances[source_id].arguments[relation] = self.instances[target_id]
    
    def set_root(self, instance_id: str):
        """Set the root instance of the graph"""
        if instance_id in self.instances:
            self.root = instance_id
    
    def get_semantic_roles(self, predicate_id: str) -> Dict[AMRRelation, str]:
        """Get all semantic roles for a predicate"""
        roles = {}
        for source, relation, target in self.edges:
            if source == predicate_id:
                roles[relation] = target
        return roles
    
    def to_penman(self) -> str:
        """Convert to PENMAN notation for debugging"""
        if not self.root:
            return ""
        
        def format_instance(instance_id: str, visited: Set[str]) -> str:
            if instance_id in visited:
                return instance_id
            
            visited.add(instance_id)
            instance = self.instances[instance_id]
            result = f"({instance_id} / {instance.concept.name}"
            
            # Add arguments
            for relation, target in instance.arguments.items():
                result += f"\n      :{relation.value} {format_instance(target.instance_id, visited)}"
            
            result += ")"
            return result
        
        return format_instance(self.root, set())


class AMRConceptLibrary:
    """
    Library of AMR concepts for TCE predicates and operators.
    
    Maps common TCE patterns to their semantic representations.
    """
    
    def __init__(self):
        self.concepts: Dict[str, AMRConcept] = {}
        self._init_builtin_concepts()
    
    def _init_builtin_concepts(self):
        """Initialize built-in AMR concepts for TCE"""
        # Mathematical predicates
        self.concepts["equal"] = AMRConcept(
            name="equal-01",
            frame_type="predicate",
            roles=[AMRRelation.ARG1, AMRRelation.ARG2],
            constraints={"arity": 2, "types": ["number", "number"]}
        )
        
        self.concepts["greater"] = AMRConcept(
            name="greater-than-01", 
            frame_type="predicate",
            roles=[AMRRelation.ARG1, AMRRelation.ARG2],
            constraints={"arity": 2, "types": ["number", "number"]}
        )
        
        # Logical operators
        self.concepts["and"] = AMRConcept(
            name="and",
            frame_type="operator",
            roles=[AMRRelation.ARG1, AMRRelation.ARG2],
            constraints={"arity": 2, "types": ["boolean", "boolean"]}
        )
        
        self.concepts["or"] = AMRConcept(
            name="or",
            frame_type="operator", 
            roles=[AMRRelation.ARG1, AMRRelation.ARG2],
            constraints={"arity": 2, "types": ["boolean", "boolean"]}
        )
        
        # Quantifiers
        self.concepts["forall"] = AMRConcept(
            name="every",
            frame_type="quantifier",
            roles=[AMRRelation.ARG1, AMRRelation.SCOPE, AMRRelation.DOMAIN],
            constraints={"quantifier": "universal"}
        )
        
        self.concepts["exists"] = AMRConcept(
            name="some",
            frame_type="quantifier", 
            roles=[AMRRelation.ARG1, AMRRelation.SCOPE, AMRRelation.DOMAIN],
            constraints={"quantifier": "existential"}
        )
        
        # Domain-specific predicates (can be extended)
        self.concepts["prime"] = AMRConcept(
            name="prime-number",
            frame_type="predicate",
            roles=[AMRRelation.ARG1],
            constraints={"arity": 1, "domain": "mathematics"}
        )
        
        self.concepts["even"] = AMRConcept(
            name="even-number",
            frame_type="predicate",
            roles=[AMRRelation.ARG1], 
            constraints={"arity": 1, "domain": "mathematics"}
        )
    
    def get_concept(self, predicate_name: str) -> Optional[AMRConcept]:
        """Get AMR concept for a predicate name"""
        # Try exact match first
        if predicate_name in self.concepts:
            return self.concepts[predicate_name]
        
        # Try pattern matching for variations
        for concept_name, concept in self.concepts.items():
            if self._matches_pattern(predicate_name, concept_name):
                return concept
        
        return None
    
    def _matches_pattern(self, predicate: str, concept: str) -> bool:
        """Check if predicate matches concept pattern"""
        # Simple fuzzy matching - could be enhanced with edit distance
        predicate_clean = re.sub(r'[^a-zA-Z]', '', predicate.lower())
        concept_clean = re.sub(r'[^a-zA-Z]', '', concept.lower())
        
        return predicate_clean in concept_clean or concept_clean in predicate_clean


class AMRSemanticAnalyzer:
    """
    Main AMR semantic analyzer for TCE.
    
    Converts AST nodes to AMR graphs with semantic role labeling.
    Provides enhanced semantic understanding beyond basic parsing.
    """
    
    def __init__(self):
        self.concept_library = AMRConceptLibrary()
        self.instance_counter = 0
        
    def analyze(self, ast_node: ASTNode) -> AMRGraph:
        """
        Convert AST to AMR graph with semantic analysis.
        
        Args:
            ast_node: Root AST node from CNL parser
            
        Returns:
            AMRGraph with semantic role labeling
        """
        graph = AMRGraph()
        self.instance_counter = 0
        
        root_id = self._process_node(ast_node, graph)
        if root_id:
            graph.set_root(root_id)
        
        return graph
    
    def _process_node(self, node: ASTNode, graph: AMRGraph) -> Optional[str]:
        """Process a single AST node into AMR representation"""
        if isinstance(node, PredicateCallNode):
            return self._process_predicate(node, graph)
        elif isinstance(node, QuantifierBlockNode):
            return self._process_quantifier(node, graph)
        elif isinstance(node, VariableNode):
            return self._process_variable(node, graph)
        else:
            # Handle CNLParser node types
            return self._process_cnl_node(node, graph)
    
    def _process_predicate(self, node: PredicateCallNode, graph: AMRGraph) -> str:
        """Process predicate call into AMR instance"""
        concept = self.concept_library.get_concept(node.name)
        if not concept:
            # Create generic concept for unknown predicates
            concept = AMRConcept(
                name=f"{node.name}-01",
                frame_type="predicate",
                roles=[AMRRelation.ARG0, AMRRelation.ARG1][:len(node.args)],
                constraints={"arity": len(node.args)}
            )
        
        instance_id = f"p{self.instance_counter}"
        self.instance_counter += 1
        
        instance = graph.add_instance(instance_id, concept)
        
        # Process arguments and assign semantic roles
        for i, arg in enumerate(node.args):
            if i < len(concept.roles):
                role = concept.roles[i]
                arg_id = self._process_node(arg, graph)
                if arg_id:
                    graph.add_edge(instance_id, role, arg_id)
        
        return instance_id
    
    def _process_quantifier(self, node: QuantifierBlockNode, graph: AMRGraph) -> str:
        """Process quantifier block into AMR representation"""
        concept = self.concept_library.get_concept(node.quant_type)
        if not concept:
            concept = AMRConcept(
                name=node.quant_type,
                frame_type="quantifier",
                roles=[AMRRelation.ARG1, AMRRelation.SCOPE],
                constraints={"quantifier": node.quant_type}
            )
        
        instance_id = f"q{self.instance_counter}"
        self.instance_counter += 1
        
        instance = graph.add_instance(instance_id, concept)
        
        # Process quantified variables
        for var in node.variables:
            var_id = self._process_variable(var, graph)
            if var_id:
                graph.add_edge(instance_id, AMRRelation.ARG1, var_id)
        
        # Process scope condition
        if node.condition:
            scope_id = self._process_node(node.condition, graph)
            if scope_id:
                graph.add_edge(instance_id, AMRRelation.SCOPE, scope_id)
        
        return instance_id
    
    def _process_variable(self, node: VariableNode, graph: AMRGraph) -> str:
        """Process variable into AMR representation"""
        # Variables become entities in AMR
        concept = AMRConcept(
            name="thing",
            frame_type="entity",
            roles=[],
            constraints={"variable": node.name}
        )
        
        instance_id = f"x{self.instance_counter}"
        self.instance_counter += 1
        
        graph.add_instance(instance_id, concept)
        graph.variables.add(node.name)
        
        return instance_id
    
    def _process_cnl_node(self, node, graph: AMRGraph) -> Optional[str]:
        """
        Process CNLParser node types using strategy pattern.
        
        This method dispatches to specialized handlers for each node type,
        following the Single Responsibility Principle and reducing complexity.
        
        Args:
            node: CNL parser node to process
            graph: AMR graph to add instances to
            
        Returns:
            Optional[str]: Instance ID of created AMR node, or None if processing failed
        """
        node_type = type(node).__name__
        
        # Dispatch to appropriate handler based on node type
        handler_map = {
            "SentenceNode": self._handle_sentence_node,
            "FactNode": self._handle_fact_node,
            "ComparisonNode": self._handle_comparison_node,
            "ConstantNode": self._handle_constant_node,
        }
        
        handler = handler_map.get(node_type, self._handle_unknown_node)
        return handler(node, graph)
    
    def _handle_sentence_node(self, node, graph: AMRGraph) -> Optional[str]:
        """Handle SentenceNode by extracting and processing its content."""
        if hasattr(node, 'content'):
            return self._process_cnl_node(node.content, graph)
        return None
    
    def _handle_fact_node(self, node, graph: AMRGraph) -> Optional[str]:
        """Handle FactNode by extracting and processing its statement."""
        if hasattr(node, 'statement'):
            return self._process_cnl_node(node.statement, graph)
        return None
    
    def _handle_comparison_node(self, node, graph: AMRGraph) -> Optional[str]:
        """
        Handle ComparisonNode by creating a comparison concept with operands.
        
        Creates an AMR concept for the comparison operation and links
        the left and right operands as arguments.
        """
        # Create comparison concept
        concept = AMRConcept(
            name=f"compare-{node.operator}",
            frame_type="predicate",
            roles=[AMRRelation.ARG1, AMRRelation.ARG2],
            constraints={"operator": node.operator}
        )
        
        instance_id = self._generate_instance_id("c")
        graph.add_instance(instance_id, concept)
        
        # Process and link operands
        self._link_comparison_operands(node, graph, instance_id)
        
        return instance_id
    
    def _handle_constant_node(self, node, graph: AMRGraph) -> Optional[str]:
        """
        Handle ConstantNode by creating an entity concept.
        
        Creates an AMR concept representing a constant value
        with its type and value as constraints.
        """
        concept = AMRConcept(
            name=f"constant-{node.value_type.lower()}",
            frame_type="entity",
            roles=[],
            constraints={"value": node.value, "type": node.value_type}
        )
        
        instance_id = self._generate_instance_id("k")
        graph.add_instance(instance_id, concept)
        
        return instance_id
    
    def _handle_unknown_node(self, node, graph: AMRGraph) -> Optional[str]:
        """
        Handle unknown node types by creating a generic concept.
        
        This provides graceful degradation for node types not yet
        explicitly supported by the AMR processor.
        """
        node_type = type(node).__name__
        
        concept = AMRConcept(
            name=f"unknown-{node_type.lower()}",
            frame_type="entity",
            roles=[],
            constraints={"node_type": node_type}
        )
        
        instance_id = self._generate_instance_id("u")
        graph.add_instance(instance_id, concept)
        
        return instance_id
    
    def _generate_instance_id(self, prefix: str) -> str:
        """
        Generate a unique instance ID with the given prefix.
        
        Args:
            prefix: Single character prefix for the instance ID
            
        Returns:
            str: Unique instance ID like "c0", "k1", "u2", etc.
        """
        instance_id = f"{prefix}{self.instance_counter}"
        self.instance_counter += 1
        return instance_id
    
    def _link_comparison_operands(self, node, graph: AMRGraph, instance_id: str) -> None:
        """
        Process and link the left and right operands of a comparison node.
        
        Args:
            node: Comparison node with 'left' and 'right' attributes
            graph: AMR graph to add edges to
            instance_id: ID of the comparison instance to link operands to
        """
        # Process left operand
        if hasattr(node, 'left'):
            left_id = self._process_cnl_node(node.left, graph)
            if left_id:
                graph.add_edge(instance_id, AMRRelation.ARG1, left_id)
        
        # Process right operand  
        if hasattr(node, 'right'):
            right_id = self._process_cnl_node(node.right, graph)
            if right_id:
                graph.add_edge(instance_id, AMRRelation.ARG2, right_id)
    
    def get_semantic_roles(self, graph: AMRGraph, predicate_name: str) -> List[Dict[str, Any]]:
        """
        Extract semantic roles for analysis.
        
        Returns list of role assignments with confidence scores.
        """
        roles = []
        
        for instance_id, instance in graph.instances.items():
            if instance.concept.name.startswith(predicate_name):
                for relation, target in instance.arguments.items():
                    roles.append({
                        "predicate": predicate_name,
                        "role": relation.value,
                        "argument": target.concept.name,
                        "confidence": self._calculate_confidence(instance, relation)
                    })
        
        return roles
    
    def _calculate_confidence(self, instance: AMRInstance, relation: AMRRelation) -> float:
        """Calculate confidence score for role assignment"""
        # Simple heuristic - could be enhanced with machine learning
        base_confidence = 0.8
        
        # Higher confidence for standard roles
        if relation in [AMRRelation.ARG0, AMRRelation.ARG1]:
            base_confidence += 0.1
        
        # Higher confidence for known concepts
        if instance.concept.name in self.concept_library.concepts:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)


# Example usage and integration
def enhance_semantic_analysis(ast_node: ASTNode) -> Dict[str, Any]:
    """
    Enhanced semantic analysis using AMR.
    
    This function can be integrated into the existing semantic analyzer
    to provide deeper understanding of TCE semantics.
    """
    amr_analyzer = AMRSemanticAnalyzer()
    amr_graph = amr_analyzer.analyze(ast_node)
    
    return {
        "amr_graph": amr_graph,
        "semantic_roles": amr_analyzer.get_semantic_roles(amr_graph, ""),
        "penman_notation": amr_graph.to_penman(),
        "variables": list(amr_graph.variables),
        "complexity": len(amr_graph.instances)
    }