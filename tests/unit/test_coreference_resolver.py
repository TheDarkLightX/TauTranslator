"""
Unit tests for CoreferenceResolver component
Tests pronoun resolution, entity tracking, and coreference chains.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "backend/unified"))

from advanced_parsing_architecture import CoreferenceResolver, Mention, CoreferenceChain


class TestCoreferenceResolver:
    """Test suite for CoreferenceResolver."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.resolver = CoreferenceResolver()
    
    def test_add_single_mention(self):
        """Test adding a single mention creates new chain."""
        mention = Mention(
            text="John",
            start_pos=0,
            end_pos=4,
            mention_type="proper_noun",
            features={"entity_type": "person", "gender": "male"}
        )
        
        self.resolver.add_mention(mention)
        
        # Should create one chain
        assert len(self.resolver.chains) == 1
        assert len(self.resolver.chains[0].mentions) == 1
        assert self.resolver.chains[0].mentions[0] == mention
        assert self.resolver.mention_to_chain["John"] == 0
    
    def test_string_match_coreference(self):
        """Test exact string matching for coreference."""
        # First mention of "the car"
        mention1 = Mention("the car", 10, 17, "definite")
        self.resolver.add_mention(mention1)
        
        # Second mention of "the car" should link to same chain
        mention2 = Mention("the car", 50, 57, "definite")
        self.resolver.add_mention(mention2)
        
        # Should have one chain with two mentions
        assert len(self.resolver.chains) == 1
        assert len(self.resolver.chains[0].mentions) == 2
        assert self.resolver.mention_to_chain["the car"] == 0
    
    def test_pronoun_resolution(self):
        """Test pronoun resolution to antecedent."""
        # Add person mention
        person = Mention(
            text="Mary",
            start_pos=0,
            end_pos=4,
            mention_type="proper_noun",
            features={"entity_type": "person", "gender": "female"}
        )
        self.resolver.add_mention(person)
        
        # Update chain properties
        self.resolver.chains[0].entity_type = "person"
        self.resolver.chains[0].properties["gender"] = "female"
        
        # Add pronoun that should resolve to Mary
        pronoun = Mention(
            text="she",
            start_pos=20,
            end_pos=23,
            mention_type="pronoun",
            features={"gender": "female"}
        )
        self.resolver.add_mention(pronoun)
        
        # Should link to same chain
        assert len(self.resolver.chains) == 1
        assert len(self.resolver.chains[0].mentions) == 2
        assert self.resolver.mention_to_chain["she"] == 0
    
    def test_partial_string_match(self):
        """Test partial string matching."""
        # Mention "John Smith"
        full_name = Mention("John Smith", 0, 10, "proper_noun")
        self.resolver.add_mention(full_name)
        
        # Mention just "John" should match
        first_name = Mention("John", 20, 24, "proper_noun")
        self.resolver.add_mention(first_name)
        
        # Should link to same chain
        assert len(self.resolver.chains) == 1
        assert len(self.resolver.chains[0].mentions) == 2
    
    def test_number_agreement(self):
        """Test number agreement in coreference."""
        # Singular entity
        company = Mention(
            text="the company",
            start_pos=0,
            end_pos=11,
            mention_type="definite",
            features={"number": "singular"}
        )
        self.resolver.add_mention(company)
        self.resolver.chains[0].properties["number"] = "singular"
        
        # Singular pronoun should match
        it_pronoun = Mention(
            text="it",
            start_pos=30,
            end_pos=32,
            mention_type="pronoun",
            features={"number": "singular"}
        )
        self.resolver.add_mention(it_pronoun)
        
        # Plural pronoun should not match
        they_pronoun = Mention(
            text="they",
            start_pos=50,
            end_pos=54,
            mention_type="pronoun",
            features={"number": "plural"}
        )
        self.resolver.add_mention(they_pronoun)
        
        # Should have 2 chains
        assert len(self.resolver.chains) == 2
        assert self.resolver.mention_to_chain["it"] == 0
        assert self.resolver.mention_to_chain["they"] == 1
    
    def test_distance_penalty(self):
        """Test that distance affects coreference scoring."""
        # Create two potential antecedents
        car1 = Mention("a car", 0, 5, "indefinite")
        self.resolver.add_mention(car1)
        
        car2 = Mention("a car", 100, 105, "indefinite")
        self.resolver.add_mention(car2)
        
        # Pronoun close to second mention
        it_pronoun = Mention("it", 110, 112, "pronoun")
        
        # Calculate scores manually
        score1 = self.resolver._compute_chain_score(it_pronoun, self.resolver.chains[0])
        score2 = self.resolver._compute_chain_score(it_pronoun, self.resolver.chains[1])
        
        # Score for closer mention should be higher (less negative distance penalty)
        assert score2 > score1
    
    def test_feature_extraction(self):
        """Test feature extraction for coreference."""
        mention = Mention("the dog", 0, 7, "definite")
        chain = CoreferenceChain(
            entity_id="entity_1",
            mentions=[Mention("a dog", 0, 5, "indefinite")],
            entity_type="animal",
            properties={"number": "singular"}
        )
        
        features = self.resolver._extract_features(mention, chain)
        
        # Should detect partial match
        assert "partial_match" in features
        assert features["partial_match"] == 1.0
        
        # Should calculate distance
        assert "syntactic_distance" in features
    
    def test_complex_coreference_chain(self):
        """Test building complex coreference chain."""
        # "John bought a car. He loves the car. It is red."
        
        mentions = [
            Mention("John", 0, 4, "proper_noun", {"entity_type": "person", "gender": "male"}),
            Mention("a car", 12, 17, "indefinite", {"entity_type": "vehicle"}),
            Mention("He", 19, 21, "pronoun", {"gender": "male"}),
            Mention("the car", 28, 35, "definite", {"entity_type": "vehicle"}),
            Mention("It", 37, 39, "pronoun", {"entity_type": "object"})
        ]
        
        for mention in mentions:
            self.resolver.add_mention(mention)
        
        # Should create 2 chains: one for John/He, one for car/the car/It
        assert len(self.resolver.chains) == 2
        
        # Find which chain has John
        john_chain_idx = self.resolver.mention_to_chain["John"]
        car_chain_idx = self.resolver.mention_to_chain["a car"]
        
        john_chain = self.resolver.chains[john_chain_idx]
        car_chain = self.resolver.chains[car_chain_idx]
        
        # John chain should have John and He
        john_mentions = [m.text for m in john_chain.mentions]
        assert "John" in john_mentions
        assert "He" in john_mentions
        
        # Car chain should have all car references
        car_mentions = [m.text for m in car_chain.mentions]
        assert "a car" in car_mentions
        assert "the car" in car_mentions
        assert "It" in car_mentions


class TestMentionDataStructure:
    """Test the Mention dataclass."""
    
    def test_mention_creation(self):
        """Test creating mention instances."""
        mention = Mention(
            text="the president",
            start_pos=10,
            end_pos=23,
            mention_type="definite",
            features={"title": True, "animate": True}
        )
        
        assert mention.text == "the president"
        assert mention.start_pos == 10
        assert mention.end_pos == 23
        assert mention.mention_type == "definite"
        assert mention.features["title"] is True
        assert mention.features["animate"] is True
    
    def test_mention_types(self):
        """Test different mention types."""
        pronoun = Mention("he", 0, 2, "pronoun")
        assert pronoun.mention_type == "pronoun"
        
        definite = Mention("the cat", 0, 7, "definite")
        assert definite.mention_type == "definite"
        
        indefinite = Mention("a dog", 0, 5, "indefinite")
        assert indefinite.mention_type == "indefinite"
        
        proper = Mention("Alice", 0, 5, "proper_noun")
        assert proper.mention_type == "proper_noun"


class TestCoreferenceChainDataStructure:
    """Test the CoreferenceChain dataclass."""
    
    def test_chain_creation(self):
        """Test creating coreference chain."""
        chain = CoreferenceChain(
            entity_id="entity_42",
            entity_type="person"
        )
        
        assert chain.entity_id == "entity_42"
        assert chain.entity_type == "person"
        assert chain.mentions == []
        assert chain.properties == {}
    
    def test_chain_with_mentions(self):
        """Test chain with initial mentions."""
        mentions = [
            Mention("Alice", 0, 5, "proper_noun"),
            Mention("she", 20, 23, "pronoun")
        ]
        
        chain = CoreferenceChain(
            entity_id="entity_1",
            mentions=mentions,
            entity_type="person",
            properties={"gender": "female", "animate": True}
        )
        
        assert len(chain.mentions) == 2
        assert chain.mentions[0].text == "Alice"
        assert chain.mentions[1].text == "she"
        assert chain.properties["gender"] == "female"


class TestCoreferenceResolverIntegration:
    """Integration tests with realistic examples."""
    
    def test_news_article_coreference(self):
        """Test coreference in news article style text."""
        resolver = CoreferenceResolver()
        
        # "The president announced new policies. He said they would help."
        mentions = [
            Mention("The president", 0, 13, "definite", {"entity_type": "person", "title": True}),
            Mention("new policies", 23, 35, "indefinite", {"entity_type": "policy", "number": "plural"}),
            Mention("He", 37, 39, "pronoun", {"gender": "male", "number": "singular"}),
            Mention("they", 45, 49, "pronoun", {"number": "plural"})
        ]
        
        for mention in mentions:
            resolver.add_mention(mention)
        
        # Update chain properties
        if resolver.chains:
            resolver.chains[0].properties.update({"gender": "male", "number": "singular"})
            if len(resolver.chains) > 1:
                resolver.chains[1].properties.update({"number": "plural"})
        
        # Should have 2 chains
        assert len(resolver.chains) == 2
        
        # President and He should be linked
        president_chain = resolver.chains[resolver.mention_to_chain["The president"]]
        assert any(m.text == "He" for m in president_chain.mentions)
        
        # Policies and they should be linked
        policies_chain = resolver.chains[resolver.mention_to_chain["new policies"]]
        assert any(m.text == "they" for m in policies_chain.mentions)
    
    def test_technical_document_coreference(self):
        """Test coreference in technical documentation."""
        resolver = CoreferenceResolver()
        
        # "The system processes requests. It logs each request. The request is then queued."
        mentions = [
            Mention("The system", 0, 10, "definite", {"entity_type": "system"}),
            Mention("requests", 20, 28, "indefinite", {"entity_type": "request", "number": "plural"}),
            Mention("It", 30, 32, "pronoun", {"number": "singular"}),
            Mention("each request", 37, 49, "indefinite", {"entity_type": "request", "number": "singular"}),
            Mention("The request", 51, 62, "definite", {"entity_type": "request", "number": "singular"})
        ]
        
        for mention in mentions:
            resolver.add_mention(mention)
        
        # Should create chains for system and request(s)
        assert len(resolver.chains) >= 2
        
        # "It" should refer to "The system"
        system_chain = resolver.chains[resolver.mention_to_chain["The system"]]
        assert any(m.text == "It" for m in system_chain.mentions)
    
    def test_definiteness_progression(self):
        """Test typical definiteness progression in discourse."""
        resolver = CoreferenceResolver()
        
        # "A student entered. The student sat down."
        # Typical pattern: indefinite -> definite
        
        student1 = Mention("A student", 0, 9, "indefinite", {"entity_type": "person"})
        resolver.add_mention(student1)
        
        student2 = Mention("The student", 19, 30, "definite", {"entity_type": "person"})
        resolver.add_mention(student2)
        
        # Should link due to partial match and progression pattern
        assert len(resolver.chains) == 1
        assert len(resolver.chains[0].mentions) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])