"""
Unit tests for SemanticGraph component
Tests graph construction, traversal, and semantic operations.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from advanced_parsing_architecture import SemanticGraph, SemanticNode, SemanticEdge, NodeType


class TestSemanticGraph:
    """Test suite for SemanticGraph."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.graph = SemanticGraph()
    
    def test_add_node(self):
        """Test adding nodes to semantic graph."""
        # Create a node
        node = SemanticNode(
            id="person_1",
            type=NodeType.ENTITY,
            value="person",
            attributes={"name": "John"}
        )
        
        # Add to graph
        self.graph.add_node(node)
        
        # Verify node was added
        assert "person_1" in self.graph.nodes
        assert self.graph.nodes["person_1"] == node
        assert "person_1" in self.graph.graph.nodes
    
    def test_entity_indexing(self):
        """Test entity index is maintained correctly."""
        # Add multiple entities of same type
        person1 = SemanticNode("p1", NodeType.ENTITY, "person")
        person2 = SemanticNode("p2", NodeType.ENTITY, "person")
        car1 = SemanticNode("c1", NodeType.ENTITY, "car")
        
        self.graph.add_node(person1)
        self.graph.add_node(person2)
        self.graph.add_node(car1)
        
        # Check entity index
        assert len(self.graph.entity_index["person"]) == 2
        assert "p1" in self.graph.entity_index["person"]
        assert "p2" in self.graph.entity_index["person"]
        assert len(self.graph.entity_index["car"]) == 1
        assert "c1" in self.graph.entity_index["car"]
    
    def test_add_edge(self):
        """Test adding edges between nodes."""
        # Create nodes
        person = SemanticNode("p1", NodeType.ENTITY, "person")
        car = SemanticNode("c1", NodeType.ENTITY, "car")
        
        self.graph.add_node(person)
        self.graph.add_node(car)
        
        # Create edge
        edge = SemanticEdge("p1", "c1", "owns")
        self.graph.add_edge(edge)
        
        # Verify edge
        assert self.graph.graph.has_edge("p1", "c1")
        edge_data = self.graph.graph.get_edge_data("p1", "c1")
        assert edge_data["relation"] == "owns"
    
    def test_find_paths(self):
        """Test finding paths between nodes."""
        # Create a small graph
        nodes = [
            SemanticNode("a", NodeType.ENTITY, "A"),
            SemanticNode("b", NodeType.ENTITY, "B"),
            SemanticNode("c", NodeType.ENTITY, "C"),
            SemanticNode("d", NodeType.ENTITY, "D")
        ]
        
        for node in nodes:
            self.graph.add_node(node)
        
        # Add edges: a->b->c, a->d->c
        edges = [
            SemanticEdge("a", "b", "rel1"),
            SemanticEdge("b", "c", "rel2"),
            SemanticEdge("a", "d", "rel3"),
            SemanticEdge("d", "c", "rel4")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Find paths from a to c
        paths = self.graph.find_paths("a", "c")
        assert len(paths) == 2
        assert ["a", "b", "c"] in paths
        assert ["a", "d", "c"] in paths
    
    def test_get_subgraph(self):
        """Test extracting subgraph."""
        # Create nodes
        nodes = [
            SemanticNode("p1", NodeType.ENTITY, "person"),
            SemanticNode("p2", NodeType.ENTITY, "person"),
            SemanticNode("c1", NodeType.ENTITY, "car"),
            SemanticNode("h1", NodeType.ENTITY, "house")
        ]
        
        for node in nodes:
            self.graph.add_node(node)
        
        # Add edges
        edges = [
            SemanticEdge("p1", "c1", "owns"),
            SemanticEdge("p1", "h1", "owns"),
            SemanticEdge("p2", "c1", "wants")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Extract subgraph with p1 and its connections
        subgraph = self.graph.get_subgraph({"p1", "c1", "h1"})
        
        # Verify subgraph
        assert len(subgraph.nodes) == 3
        assert "p1" in subgraph.nodes
        assert "c1" in subgraph.nodes
        assert "h1" in subgraph.nodes
        assert "p2" not in subgraph.nodes
        
        # Check edges in subgraph
        assert subgraph.graph.has_edge("p1", "c1")
        assert subgraph.graph.has_edge("p1", "h1")
        assert not subgraph.graph.has_edge("p2", "c1")
    
    def test_complex_semantic_structure(self):
        """Test building complex semantic structure."""
        # "Every person who owns a car must have insurance"
        
        # Create nodes
        person = SemanticNode("person_var", NodeType.QUANTIFIER, "all")
        car = SemanticNode("car_var", NodeType.ENTITY, "car")
        owns_rel = SemanticNode("owns_1", NodeType.RELATION, "owns")
        insurance = SemanticNode("insurance_1", NodeType.PROPERTY, "has_insurance")
        
        self.graph.add_node(person)
        self.graph.add_node(car)
        self.graph.add_node(owns_rel)
        self.graph.add_node(insurance)
        
        # Create relationships
        edges = [
            SemanticEdge("person_var", "owns_1", "subject"),
            SemanticEdge("owns_1", "car_var", "object"),
            SemanticEdge("person_var", "insurance_1", "must_have")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Verify structure
        assert len(self.graph.nodes) == 4
        assert self.graph.graph.number_of_edges() == 3
        
        # Check semantic relationships
        person_edges = list(self.graph.graph.edges("person_var", data=True))
        assert len(person_edges) == 2
        
    def test_temporal_relationships(self):
        """Test temporal relationships in graph."""
        # Create temporal nodes
        t1 = SemanticNode("t1", NodeType.TEMPORAL, "time_point", {"value": "t"})
        t2 = SemanticNode("t2", NodeType.TEMPORAL, "time_point", {"value": "t-1"})
        input_stream = SemanticNode("i1", NodeType.ENTITY, "input_stream")
        output_stream = SemanticNode("o1", NodeType.ENTITY, "output_stream")
        
        for node in [t1, t2, input_stream, output_stream]:
            self.graph.add_node(node)
        
        # Create temporal relationships
        edges = [
            SemanticEdge("i1", "t2", "at_time"),
            SemanticEdge("o1", "t1", "at_time"),
            SemanticEdge("o1", "i1", "equals")
        ]
        
        for edge in edges:
            self.graph.add_edge(edge)
        
        # Verify temporal structure
        assert self.graph.graph.has_edge("i1", "t2")
        assert self.graph.graph.has_edge("o1", "t1")
        
        # Check we can trace temporal dependencies
        paths = self.graph.find_paths("o1", "t2")
        assert len(paths) > 0  # Should find path through i1


class TestSemanticNodeOperations:
    """Test operations on semantic nodes."""
    
    def test_node_creation(self):
        """Test creating different types of nodes."""
        # Entity node
        entity = SemanticNode("e1", NodeType.ENTITY, "person", {"name": "John"})
        assert entity.id == "e1"
        assert entity.type == NodeType.ENTITY
        assert entity.value == "person"
        assert entity.attributes["name"] == "John"
        
        # Property node
        prop = SemanticNode("p1", NodeType.PROPERTY, "red")
        assert prop.type == NodeType.PROPERTY
        assert prop.value == "red"
        
        # Quantifier node
        quant = SemanticNode("q1", NodeType.QUANTIFIER, "all", scope_level=1)
        assert quant.type == NodeType.QUANTIFIER
        assert quant.scope_level == 1
    
    def test_node_hashing(self):
        """Test nodes can be used in sets/dicts."""
        node1 = SemanticNode("n1", NodeType.ENTITY, "test")
        node2 = SemanticNode("n1", NodeType.ENTITY, "test")  # Same ID
        node3 = SemanticNode("n2", NodeType.ENTITY, "test")  # Different ID
        
        # Test hashing
        node_set = {node1, node2, node3}
        assert len(node_set) == 2  # node1 and node2 should be same
        
        # Test as dict key
        node_dict = {node1: "value1", node3: "value2"}
        assert len(node_dict) == 2
        assert node_dict[node2] == "value1"  # node2 same as node1


class TestSemanticEdgeOperations:
    """Test operations on semantic edges."""
    
    def test_edge_creation(self):
        """Test creating edges with attributes."""
        edge = SemanticEdge(
            source="p1",
            target="c1",
            relation_type="owns",
            attributes={"since": "2020", "legally": True}
        )
        
        assert edge.source == "p1"
        assert edge.target == "c1"
        assert edge.relation_type == "owns"
        assert edge.attributes["since"] == "2020"
        assert edge.attributes["legally"] is True
    
    def test_edge_types(self):
        """Test different types of semantic relationships."""
        # Ownership
        owns = SemanticEdge("person", "car", "owns")
        assert owns.relation_type == "owns"
        
        # Property
        has_prop = SemanticEdge("car", "red", "has_property")
        assert has_prop.relation_type == "has_property"
        
        # Temporal
        at_time = SemanticEdge("event", "t1", "occurs_at")
        assert at_time.relation_type == "occurs_at"
        
        # Logical
        implies = SemanticEdge("condition", "consequence", "implies")
        assert implies.relation_type == "implies"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])