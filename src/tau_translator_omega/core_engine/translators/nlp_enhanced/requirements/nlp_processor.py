"""
NLP processing infrastructure for requirements analysis.

Copyright: DarkLightX / Dana Edwards
"""

import re
from typing import List, Protocol, Any
from .domain_types import SentenceText, EntityName, PredicateName


class NLPProcessor(Protocol):
    """Protocol for NLP processing implementations."""
    def process_sentences(self, text: str) -> List[SentenceText]:
        """Split text into sentences."""
        ...
    
    def extract_entities(self, sentence: str) -> List[EntityName]:
        """Extract entities from sentence."""
        ...
    
    def extract_predicates(self, sentence: str) -> List[PredicateName]:
        """Extract predicates from sentence."""
        ...


class SpacyNLPProcessor:
    """SpaCy-based NLP processor."""
    
    def __init__(self):
        """Initialize SpaCy processor."""
        self._nlp = self._load_spacy_model()
    
    def _load_spacy_model(self):
        """Load SpaCy model with fallback."""
        try:
            import spacy
            return spacy.load("en_core_web_sm")
        except (ImportError, OSError):
            return None
    
    def process_sentences(self, text: str) -> List[SentenceText]:
        """Split text into sentences using SpaCy."""
        if self._nlp:
            doc = self._nlp(text)
            return [SentenceText(sent.text.strip()) for sent in doc.sents if sent.text.strip()]
        return self._fallback_sentence_split(text)
    
    def _fallback_sentence_split(self, text: str) -> List[SentenceText]:
        """Fallback sentence splitting without SpaCy."""
        sentences = re.split(r'[.!?]+', text)
        return [SentenceText(s.strip()) for s in sentences if s.strip()]
    
    def extract_entities(self, sentence: str) -> List[EntityName]:
        """Extract entities using SpaCy NER."""
        if not self._nlp:
            return self._fallback_entity_extraction(sentence)
        
        doc = self._nlp(sentence)
        entities = [EntityName(ent.text.lower()) for ent in doc.ents]
        entities.extend([EntityName(chunk.text.lower()) for chunk in doc.noun_chunks])
        return self._filter_entities(list(set(entities)))
    
    def _fallback_entity_extraction(self, sentence: str) -> List[EntityName]:
        """Extract entities without SpaCy."""
        patterns = [
            r'\b(system|user|application|service|database|server|client)\b',
            r'\b(number|integer|value|data|input|output|request|response)\b',
            r'\b([a-z]+(?:_[a-z]+)*)\b'
        ]
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, sentence.lower())
            entities.extend([EntityName(m) for m in matches])
        return self._filter_entities(entities)
    
    def _filter_entities(self, entities: List[EntityName]) -> List[EntityName]:
        """Filter out short or common entities."""
        return [e for e in entities if len(e) > 2]
    
    def extract_predicates(self, sentence: str) -> List[PredicateName]:
        """Extract predicates using SpaCy."""
        if not self._nlp:
            return self._fallback_predicate_extraction(sentence)
        
        doc = self._nlp(sentence)
        predicates = [PredicateName(token.lemma_.lower()) 
                     for token in doc if token.pos_ in ['VERB', 'ADJ']]
        return self._filter_predicates(predicates)
    
    def _fallback_predicate_extraction(self, sentence: str) -> List[PredicateName]:
        """Extract predicates without SpaCy."""
        patterns = [
            r'\b(is|are|was|were|be|been|being)\s+(\w+)',
            r'\b(must|shall|should|will|can|may)\s+(\w+)',
            r'\b(\w+)(?:ed|ing|s)?\b'
        ]
        predicates = []
        for pattern in patterns:
            matches = re.findall(pattern, sentence.lower())
            predicates.extend(self._flatten_matches(matches))
        return self._filter_predicates([PredicateName(p) for p in predicates])
    
    def _flatten_matches(self, matches: List[Any]) -> List[str]:
        """Flatten regex match tuples."""
        flattened = []
        for match in matches:
            if isinstance(match, tuple):
                flattened.extend(match)
            else:
                flattened.append(match)
        return flattened
    
    def _filter_predicates(self, predicates: List[PredicateName]) -> List[PredicateName]:
        """Filter out common words from predicates."""
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered = [p for p in predicates if p not in common_words and len(p) > 2]
        return list(set(filtered))