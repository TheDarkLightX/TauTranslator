"""
Unit tests for Declarative TCE Parser
Tests declarative parsing capabilities and transformations.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from declarative_tce_parser import (
    DeclarativeTCEParser, DeclarativeTCETransformer, 
    DeclarativeContext, EntityInfo, RelationshipInfo, TemporalProperty
)


class TestDeclarativeContext:
    """Test DeclarativeContext data structure."""
    
    def test_context_initialization(self):
        """Test context initializes correctly."""
        context = DeclarativeContext()
        
        assert context.entities == {}
        assert context.properties == {}
        assert context.relationships == []
        assert context.constraints == []
        assert context.temporal_properties == []
    
    def test_entity_registration(self):
        """Test registering entities in context."""
        context = DeclarativeContext()
        
        entity = EntityInfo(
            name="john",
            entity_class="person",
            properties=["tall", "smart"]
        )
        
        context.entities["john"] = entity
        
        assert "john" in context.entities
        assert context.entities["john"].entity_class == "person"
        assert "tall" in context.entities["john"].properties
    
    def test_relationship_tracking(self):
        """Test tracking relationships."""
        context = DeclarativeContext()
        
        rel = RelationshipInfo(
            subject="john",
            relation="owns",
            object="car1",
            quantified=False
        )
        
        context.relationships.append(rel)
        
        assert len(context.relationships) == 1
        assert context.relationships[0].relation == "owns"
    
    def test_temporal_property_tracking(self):
        """Test tracking temporal properties."""
        context = DeclarativeContext()
        
        temp_prop = TemporalProperty(
            quantifier="always",
            property="output = input",
            stream_refs=["o1[t]", "i1[t]"]
        )
        
        context.temporal_properties.append(temp_prop)
        
        assert len(context.temporal_properties) == 1
        assert context.temporal_properties[0].quantifier == "always"


class TestDeclarativeTCETransformer:
    """Test DeclarativeTCETransformer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.transformer = DeclarativeTCETransformer()
    
    def test_transformer_initialization(self):
        """Test transformer initializes correctly."""
        assert self.transformer is not None
        assert isinstance(self.transformer.context, DeclarativeContext)
    
    def test_fact_processing_is_property(self):
        """Test processing 'X is Y' facts."""
        # Simulate parse tree items
        items = [
            Mock(value="john"),  # entity
            Mock(type="IS"),     # operator
            Mock(value="tall")   # property
        ]
        
        result = self.transformer.fact(items)
        
        assert result is not None
        assert result['type'] == 'property'
        assert result['tau'] == 'john_is_tall'
    
    def test_fact_processing_has_property(self):
        """Test processing 'X has Y' facts."""
        items = [
            Mock(value="car"),
            Mock(type="HAS"),
            Mock(value="wheels")
        ]
        
        result = self.transformer.fact(items)
        
        assert result['type'] == 'property'
        assert result['tau'] == 'has(car, wheels)'
    
    def test_fact_processing_comparison(self):
        """Test processing comparison facts."""
        items = [
            Mock(value="x"),
            Mock(type="GREATER_THAN", value=">"),
            Mock(value="5")
        ]
        
        # Need to mock the comparison mapping
        with patch.object(self.transformer, '_map_comparison_op', return_value='>'):
            result = self.transformer.fact(items)
        
        assert result['type'] == 'constraint'
        assert 'x > 5' in result['tau']
    
    def test_quantified_property_all(self):
        """Test processing 'all X are Y'."""
        items = [
            Mock(type="ALL", value="all"),
            Mock(type="NOUN", value="cats"),
            {'tau': 'is_animals'}  # property_clause result
        ]
        
        result = self.transformer.quantified_property(items)
        
        assert result is not None
        assert result['type'] == 'property'
        assert 'all c:' in result['tau']
        assert 'is_cat(c)' in result['tau']
        assert 'is_animals' in result['tau']
    
    def test_quantified_property_no(self):
        """Test processing 'no X is Y'."""
        items = [
            Mock(type="NO", value="no"),
            Mock(type="NOUN", value="bird"),
            {'tau': 'is_mammal'}
        ]
        
        result = self.transformer.quantified_property(items)
        
        assert result['tau']
        assert '!' in result['tau']  # negation
        assert 'is_bird' in result['tau']
    
    def test_relationship_processing(self):
        """Test processing relationships."""
        items = [
            "john",
            "owns",
            "car"
        ]
        
        result = self.transformer.relationship(items)
        
        assert result['type'] == 'property'
        assert result['tau'] == 'owns(john, car)'
        
        # Check relationship was tracked
        assert len(self.transformer.context.relationships) == 1
        assert self.transformer.context.relationships[0].subject == "john"
    
    def test_temporal_property_always(self):
        """Test processing 'always' temporal properties."""
        items = [
            Mock(value="always"),
            {'tau': 'x = y'}
        ]
        
        result = self.transformer.temporal_property(items)
        
        assert result['type'] == 'temporal'
        assert '□' in result['tau'] or 'always' in result['tau']
        assert 'x = y' in result['tau']
    
    def test_temporal_property_never(self):
        """Test processing 'never' temporal properties."""
        items = [
            Mock(value="never"),
            {'tau': 'system_fails'}
        ]
        
        result = self.transformer.temporal_property(items)
        
        assert '□(!(system_fails))' in result['tau']
    
    def test_stream_property(self):
        """Test processing stream properties."""
        items = [
            "o1[t]",
            "equals",
            "i1[t]"
        ]
        
        result = self.transformer.stream_property(items)
        
        assert result['tau'] == "o1[t] = i1[t]"
    
    def test_logical_expression_and(self):
        """Test processing AND expressions."""
        items = [
            {'tau': 'A'},
            Mock(value="and"),
            {'tau': 'B'}
        ]
        
        result = self.transformer.logical_expr(items)
        
        assert '(A && B)' in result['tau']
    
    def test_logical_expression_not(self):
        """Test processing NOT expressions."""
        items = [
            Mock(value="not"),
            {'tau': 'P'}
        ]
        
        result = self.transformer.logical_expr(items)
        
        assert '!(P)' in result['tau']
    
    def test_entity_tracking(self):
        """Test entity registration and tracking."""
        items = [
            Mock(type="NOUN", value="person"),
            "john"
        ]
        
        result = self.transformer.entity(items)
        
        assert result == "john"
        assert "john" in self.transformer.context.entities
        assert self.transformer.context.entities["john"].entity_class == "person"
    
    def test_comparison_operator_mapping(self):
        """Test comparison operator mapping."""
        test_cases = [
            (Mock(value="equals"), "="),
            (Mock(value="greater than"), ">"),
            (Mock(value="less than"), "<"),
            (Mock(value="at most"), "<="),
            (Mock(value="at least"), ">=")
        ]
        
        for token, expected in test_cases:
            result = self.transformer._map_comparison_op(token)
            assert result == expected


class TestDeclarativeTCEParser:
    """Test DeclarativeTCEParser integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = DeclarativeTCEParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly."""
        assert self.parser is not None
        assert self.parser.parser is not None
    
    def test_simple_fact_parsing(self):
        """Test parsing simple facts."""
        # Would require full grammar loaded
        # This is more of an integration test
        pass
    
    def test_inline_grammar_fallback(self):
        """Test inline grammar is available."""
        grammar = self.parser._get_inline_grammar()
        
        assert grammar is not None
        assert "start" in grammar
        assert "fact" in grammar
        assert "property" in grammar


class TestEntityInfo:
    """Test EntityInfo data structure."""
    
    def test_entity_creation(self):
        """Test creating entity info."""
        entity = EntityInfo(
            name="car1",
            entity_class="vehicle"
        )
        
        assert entity.name == "car1"
        assert entity.entity_class == "vehicle"
        assert entity.properties == []
        assert entity.relationships == {}
    
    def test_entity_with_properties(self):
        """Test entity with properties."""
        entity = EntityInfo(
            name="john",
            entity_class="person",
            properties=["tall", "smart", "friendly"]
        )
        
        assert len(entity.properties) == 3
        assert "smart" in entity.properties
    
    def test_entity_relationships(self):
        """Test entity relationships."""
        entity = EntityInfo(
            name="john",
            entity_class="person"
        )
        
        entity.relationships["owns"] = ["car1", "house1"]
        entity.relationships["works_at"] = ["company1"]
        
        assert len(entity.relationships) == 2
        assert "car1" in entity.relationships["owns"]


class TestRelationshipInfo:
    """Test RelationshipInfo data structure."""
    
    def test_relationship_creation(self):
        """Test creating relationship info."""
        rel = RelationshipInfo(
            subject="alice",
            relation="teaches",
            object="math101"
        )
        
        assert rel.subject == "alice"
        assert rel.relation == "teaches"
        assert rel.object == "math101"
        assert rel.quantified is False
    
    def test_quantified_relationship(self):
        """Test quantified relationship."""
        rel = RelationshipInfo(
            subject="professor",
            relation="teaches",
            object="course",
            quantified=True
        )
        
        assert rel.quantified is True


class TestTemporalProperty:
    """Test TemporalProperty data structure."""
    
    def test_temporal_property_creation(self):
        """Test creating temporal property."""
        prop = TemporalProperty(
            quantifier="always",
            property="system_stable"
        )
        
        assert prop.quantifier == "always"
        assert prop.property == "system_stable"
        assert prop.stream_refs == []
    
    def test_temporal_with_streams(self):
        """Test temporal property with stream references."""
        prop = TemporalProperty(
            quantifier="eventually",
            property="output_ready",
            stream_refs=["o1[t]", "o2[t]"]
        )
        
        assert len(prop.stream_refs) == 2
        assert "o1[t]" in prop.stream_refs


class TestDeclarativeIntegration:
    """Integration tests for declarative parsing."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Use the enhanced parser that includes declarative capabilities
        from declarative_tce_parser import enhance_existing_tce_parser
        self.parser = enhance_existing_tce_parser()
    
    def test_declarative_patterns(self):
        """Test various declarative patterns."""
        test_cases = [
            "all persons are mortal.",
            "socrates is a person.",
            "every car has wheels.",
            "no bird is a fish.",
            "john owns a car.",
            "always output equals input.",
            "x is greater than 0."
        ]
        
        for sentence in test_cases:
            result = self.parser.parse(sentence)
            assert result is not None
            assert len(result) > 0
    
    def test_complex_declarative(self):
        """Test complex declarative sentences."""
        sentences = [
            "all prime numbers greater than 2 are odd.",
            "every student who passes all exams graduates.",
            "the system maintains consistency at all times."
        ]
        
        for sentence in sentences:
            result = self.parser.parse(sentence)
            assert result
            # Should transform to formal notation
            assert any(keyword in result.lower() for keyword in 
                      ['all', '∀', 'every', '->'])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])