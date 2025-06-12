"""
Dictionary Builder Tool - Helps create initial dictionaries from sample text
Analyzes documents to suggest entities, verbs, and patterns.

Copyright: DarkLightX / Dana Edwards
"""

import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import nltk


@dataclass
class VocabularyAnalysis:
    """Results of vocabulary analysis."""
    entities: Dict[str, Dict[str, any]] = field(default_factory=dict)
    verbs: Dict[str, Dict[str, any]] = field(default_factory=dict)
    patterns: List[Dict[str, any]] = field(default_factory=list)
    noun_phrases: Counter = field(default_factory=Counter)
    verb_phrases: Counter = field(default_factory=Counter)
    abbreviations: Dict[str, str] = field(default_factory=dict)


class DictionaryBuilder:
    """
    Helps build initial dictionaries by analyzing sample text.
    """
    
    def __init__(self):
        """Initialize the builder."""
        # Try to download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading required NLTK data...")
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('maxent_ne_chunker')
            nltk.download('words')
        
        # Common patterns to look for
        self.patterns = {
            'time_duration': r'\b(?:for|in|within)\s+(\d+)\s+(seconds?|minutes?|hours?|days?|weeks?|months?|years?)',
            'percentage': r'(\d+(?:\.\d+)?)\s*%',
            'money': r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',
            'comparison': r'(?:more|less|greater|fewer)\s+than\s+(\d+)',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}',
        }
        
        # Entity type indicators
        self.entity_indicators = {
            'person': ['who', 'person', 'people', 'employee', 'user', 'customer', 'client', 'manager', 'staff'],
            'system': ['system', 'application', 'service', 'platform', 'software', 'database', 'server'],
            'document': ['document', 'file', 'report', 'form', 'record', 'certificate', 'invoice'],
            'object': ['product', 'item', 'device', 'equipment', 'asset', 'resource'],
            'location': ['location', 'place', 'site', 'office', 'branch', 'department'],
            'event': ['event', 'meeting', 'transaction', 'process', 'activity', 'operation']
        }
    
    def analyze_text(self, text: str) -> VocabularyAnalysis:
        """Analyze text to extract vocabulary."""
        analysis = VocabularyAnalysis()
        
        # Clean and prepare text
        sentences = nltk.sent_tokenize(text)
        
        # Extract various components
        self._extract_entities(sentences, analysis)
        self._extract_verbs(sentences, analysis)
        self._extract_patterns(text, analysis)
        self._extract_abbreviations(text, analysis)
        self._extract_phrases(sentences, analysis)
        
        return analysis
    
    def _extract_entities(self, sentences: List[str], analysis: VocabularyAnalysis):
        """Extract potential entities from sentences."""
        all_nouns = []
        
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            pos_tags = nltk.pos_tag(tokens)
            
            # Extract nouns
            for word, pos in pos_tags:
                if pos in ['NN', 'NNS', 'NNP', 'NNPS']:  # Various noun types
                    normalized = word.lower()
                    if len(normalized) > 2:  # Skip very short words
                        all_nouns.append(normalized)
                        
                        # Try to determine entity type
                        entity_type = self._guess_entity_type(normalized, sentence)
                        
                        if normalized not in analysis.entities:
                            analysis.entities[normalized] = {
                                'category': entity_type,
                                'occurrences': 0,
                                'contexts': []
                            }
                        
                        analysis.entities[normalized]['occurrences'] += 1
                        analysis.entities[normalized]['contexts'].append(sentence[:100])
        
        # Identify plural forms
        self._identify_plurals(analysis.entities)
    
    def _extract_verbs(self, sentences: List[str], analysis: VocabularyAnalysis):
        """Extract potential verbs from sentences."""
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            pos_tags = nltk.pos_tag(tokens)
            
            for i, (word, pos) in enumerate(pos_tags):
                if pos.startswith('VB'):  # Verb
                    normalized = word.lower()
                    if len(normalized) > 2:
                        if normalized not in analysis.verbs:
                            analysis.verbs[normalized] = {
                                'tense': self._guess_tense(pos),
                                'occurrences': 0,
                                'typical_subjects': [],
                                'typical_objects': []
                            }
                        
                        analysis.verbs[normalized]['occurrences'] += 1
                        
                        # Try to find subject and object
                        if i > 0:
                            subject = pos_tags[i-1][0].lower()
                            if subject in analysis.entities:
                                analysis.verbs[normalized]['typical_subjects'].append(subject)
                        
                        if i < len(pos_tags) - 1:
                            obj = pos_tags[i+1][0].lower()
                            if obj in analysis.entities:
                                analysis.verbs[normalized]['typical_objects'].append(obj)
    
    def _extract_patterns(self, text: str, analysis: VocabularyAnalysis):
        """Extract common patterns from text."""
        for pattern_name, pattern_regex in self.patterns.items():
            matches = re.findall(pattern_regex, text, re.IGNORECASE)
            if matches:
                analysis.patterns.append({
                    'name': pattern_name,
                    'pattern': pattern_regex,
                    'examples': list(set(matches[:5])),  # Up to 5 unique examples
                    'count': len(matches)
                })
    
    def _extract_abbreviations(self, text: str, analysis: VocabularyAnalysis):
        """Extract potential abbreviations."""
        # Look for patterns like "API (Application Programming Interface)"
        abbrev_pattern = r'\b([A-Z]{2,})\s*\(([^)]+)\)'
        matches = re.findall(abbrev_pattern, text)
        
        for abbrev, expansion in matches:
            analysis.abbreviations[abbrev] = expansion
        
        # Also look for common uppercase sequences
        uppercase_pattern = r'\b[A-Z]{2,6}\b'
        uppercase_words = re.findall(uppercase_pattern, text)
        
        for word in uppercase_words:
            if word not in analysis.abbreviations and len(word) <= 5:
                # Mark as potential abbreviation
                analysis.abbreviations[word] = f"[Unknown - {word}]"
    
    def _extract_phrases(self, sentences: List[str], analysis: VocabularyAnalysis):
        """Extract common noun and verb phrases."""
        for sentence in sentences:
            tokens = nltk.word_tokenize(sentence)
            pos_tags = nltk.pos_tag(tokens)
            
            # Extract noun phrases (simple approach)
            i = 0
            while i < len(pos_tags):
                if pos_tags[i][1] in ['DT', 'JJ']:  # Determiner or adjective
                    phrase_parts = []
                    j = i
                    while j < len(pos_tags) and pos_tags[j][1] in ['DT', 'JJ', 'NN', 'NNS']:
                        phrase_parts.append(pos_tags[j][0])
                        j += 1
                    
                    if len(phrase_parts) > 1:
                        phrase = ' '.join(phrase_parts).lower()
                        analysis.noun_phrases[phrase] += 1
                    i = j
                else:
                    i += 1
    
    def _guess_entity_type(self, word: str, context: str) -> str:
        """Guess the entity type based on word and context."""
        context_lower = context.lower()
        
        for entity_type, indicators in self.entity_indicators.items():
            for indicator in indicators:
                if indicator in word or indicator in context_lower:
                    return entity_type
        
        # Default guesses based on common patterns
        if word.endswith('er') or word.endswith('or'):  # Often person roles
            return 'person'
        elif word.endswith('tion') or word.endswith('ment'):  # Often events/abstract
            return 'event'
        else:
            return 'object'
    
    def _guess_tense(self, pos_tag: str) -> str:
        """Guess verb tense from POS tag."""
        tense_map = {
            'VB': 'base',
            'VBD': 'past',
            'VBG': 'gerund',
            'VBN': 'past_participle',
            'VBP': 'present',
            'VBZ': 'present_3rd'
        }
        return tense_map.get(pos_tag, 'unknown')
    
    def _identify_plurals(self, entities: Dict[str, Dict]):
        """Identify likely plural forms."""
        for entity in list(entities.keys()):
            # Check common plural patterns
            if entity.endswith('s') and not entity.endswith('ss'):
                singular = entity[:-1]
                if singular in entities:
                    entities[singular]['plural_form'] = entity
                elif entity.endswith('ies'):
                    singular = entity[:-3] + 'y'
                    if singular in entities:
                        entities[singular]['plural_form'] = entity
                elif entity.endswith('es'):
                    singular = entity[:-2]
                    if singular in entities:
                        entities[singular]['plural_form'] = entity
    
    def generate_dictionary(self, analysis: VocabularyAnalysis, 
                          threshold: int = 2) -> Dict[str, any]:
        """Generate dictionary from analysis results."""
        dictionary = {
            'entities': {},
            'verbs': {},
            'patterns': [],
            'abbreviations': {}
        }
        
        # Filter entities by occurrence threshold
        for entity, info in analysis.entities.items():
            if info['occurrences'] >= threshold:
                dictionary['entities'][entity] = {
                    'category': info['category']
                }
                if 'plural_form' in info:
                    dictionary['entities'][entity]['plural_form'] = info['plural_form']
        
        # Filter verbs by occurrence threshold
        for verb, info in analysis.verbs.items():
            if info['occurrences'] >= threshold:
                verb_entry = {}
                
                # Add common subjects/objects if found
                if info['typical_subjects']:
                    subjects = Counter(info['typical_subjects']).most_common(3)
                    verb_entry['typical_subjects'] = [s[0] for s in subjects]
                
                if info['typical_objects']:
                    objects = Counter(info['typical_objects']).most_common(3)
                    verb_entry['typical_objects'] = [o[0] for o in objects]
                
                if verb_entry:
                    dictionary['verbs'][verb] = verb_entry
        
        # Add patterns that appear frequently
        for pattern in analysis.patterns:
            if pattern['count'] >= 2:
                dictionary['patterns'].append({
                    'name': pattern['name'],
                    'pattern': pattern['pattern'],
                    'examples': pattern['examples'][:3]
                })
        
        # Add abbreviations (excluding unknowns)
        dictionary['abbreviations'] = {
            k: v for k, v in analysis.abbreviations.items() 
            if not v.startswith('[Unknown')
        }
        
        return dictionary
    
    def save_dictionary(self, dictionary: Dict, filepath: Path, 
                       format: str = 'yaml'):
        """Save dictionary to file."""
        if format == 'yaml':
            with open(filepath, 'w') as f:
                yaml.dump(dictionary, f, default_flow_style=False, 
                         allow_unicode=True, sort_keys=False)
        elif format == 'json':
            with open(filepath, 'w') as f:
                json.dump(dictionary, f, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def print_analysis_summary(self, analysis: VocabularyAnalysis):
        """Print summary of analysis results."""
        print("\n📊 Vocabulary Analysis Summary")
        print("=" * 50)
        
        print(f"\n📝 Entities found: {len(analysis.entities)}")
        # Top entities by occurrence
        top_entities = sorted(analysis.entities.items(), 
                            key=lambda x: x[1]['occurrences'], 
                            reverse=True)[:10]
        for entity, info in top_entities:
            print(f"  - {entity} ({info['category']}): {info['occurrences']} times")
        
        print(f"\n🔧 Verbs found: {len(analysis.verbs)}")
        top_verbs = sorted(analysis.verbs.items(), 
                         key=lambda x: x[1]['occurrences'], 
                         reverse=True)[:10]
        for verb, info in top_verbs:
            print(f"  - {verb}: {info['occurrences']} times")
        
        print(f"\n🎯 Patterns found: {len(analysis.patterns)}")
        for pattern in analysis.patterns:
            print(f"  - {pattern['name']}: {pattern['count']} matches")
        
        print(f"\n📝 Common phrases:")
        for phrase, count in analysis.noun_phrases.most_common(5):
            if count > 1:
                print(f"  - '{phrase}': {count} times")
        
        print(f"\n🔤 Abbreviations found: {len(analysis.abbreviations)}")
        for abbrev, expansion in list(analysis.abbreviations.items())[:5]:
            print(f"  - {abbrev}: {expansion}")


def main():
    """Example usage of dictionary builder."""
    # Example text for analysis
    sample_text = """
    All employees must submit their timesheets by Friday. Each employee who works 
    on multiple projects should allocate their hours accordingly. The HR department 
    processes all timesheets and calculates overtime payments.
    
    Managers review and approve timesheets before they are sent to payroll. 
    Any timesheet submitted after the deadline requires manager approval and may 
    delay payment processing.
    
    The system automatically validates timesheet entries and flags any discrepancies. 
    Employees receive notifications about their timesheet status via email.
    
    For questions about timesheet policies, employees should contact their direct 
    manager or the HR department. The company maintains detailed records of all 
    timesheet submissions for audit purposes.
    """
    
    # Create builder and analyze
    builder = DictionaryBuilder()
    analysis = builder.analyze_text(sample_text)
    
    # Print summary
    builder.print_analysis_summary(analysis)
    
    # Generate dictionary
    dictionary = builder.generate_dictionary(analysis, threshold=1)
    
    # Save to file
    output_path = Path("extracted_dictionary.yaml")
    builder.save_dictionary(dictionary, output_path)
    print(f"\n✅ Dictionary saved to: {output_path}")
    
    # Show generated dictionary
    print("\n📚 Generated Dictionary:")
    print(yaml.dump(dictionary, default_flow_style=False))


if __name__ == "__main__":
    main()