"""
User Dictionary System - Extensible vocabulary for TCE Parser
Allows users to add custom words, entities, and domain-specific patterns.

Copyright: DarkLightX / Dana Edwards
"""

import json
import yaml
import csv
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging


@dataclass
class UserEntity:
    """User-defined entity with properties."""
    name: str
    category: str  # person, object, system, etc.
    plural_form: Optional[str] = None
    properties: List[str] = field(default_factory=list)
    synonyms: List[str] = field(default_factory=list)
    typical_verbs: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {k: v for k, v in asdict(self).items() if v}


@dataclass
class UserVerb:
    """User-defined verb/action."""
    verb: str
    past_tense: Optional[str] = None
    synonyms: List[str] = field(default_factory=list)
    typical_subjects: List[str] = field(default_factory=list)
    typical_objects: List[str] = field(default_factory=list)
    prepositions: List[str] = field(default_factory=list)  # e.g., "reports to", "works for"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {k: v for k, v in asdict(self).items() if v}


@dataclass
class UserPattern:
    """User-defined pattern for complex expressions."""
    name: str
    pattern: str  # regex pattern
    replacement: str  # what to replace with
    description: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {k: v for k, v in asdict(self).items() if v}


@dataclass
class DomainVocabulary:
    """Domain-specific vocabulary set."""
    domain: str  # e.g., "healthcare", "finance", "legal"
    entities: Dict[str, UserEntity] = field(default_factory=dict)
    verbs: Dict[str, UserVerb] = field(default_factory=dict)
    patterns: Dict[str, UserPattern] = field(default_factory=dict)
    abbreviations: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain,
            "entities": {k: v.to_dict() for k, v in self.entities.items()},
            "verbs": {k: v.to_dict() for k, v in self.verbs.items()},
            "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
            "abbreviations": self.abbreviations
        }


class UserDictionary:
    """
    Extensible user dictionary system.
    Supports loading from multiple file formats and runtime additions.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with optional base path for dictionary files."""
        self.logger = logging.getLogger(__name__)
        self.base_path = base_path or Path.home() / ".tau_translator" / "dictionaries"
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Core dictionaries
        self.entities: Dict[str, UserEntity] = {}
        self.verbs: Dict[str, UserVerb] = {}
        self.patterns: Dict[str, UserPattern] = {}
        self.abbreviations: Dict[str, str] = {}
        
        # Domain-specific vocabularies
        self.domains: Dict[str, DomainVocabulary] = {}
        
        # Synonym mappings for quick lookup
        self.entity_synonyms: Dict[str, str] = {}  # synonym -> canonical name
        self.verb_synonyms: Dict[str, str] = {}
        
        # Load default dictionaries
        self._load_defaults()
        
    def _load_defaults(self):
        """Load default dictionary files if they exist."""
        default_files = [
            "default.yaml",
            "default.json",
            "entities.csv",
            "verbs.csv",
            "patterns.yaml"
        ]
        
        for filename in default_files:
            filepath = self.base_path / filename
            if filepath.exists():
                try:
                    self.load_from_file(filepath)
                    self.logger.info(f"Loaded default dictionary: {filename}")
                except Exception as e:
                    self.logger.error(f"Failed to load {filename}: {e}")
    
    def add_entity(self, entity: UserEntity, domain: Optional[str] = None):
        """Add a user-defined entity."""
        # Add to appropriate dictionary
        if domain:
            if domain not in self.domains:
                self.domains[domain] = DomainVocabulary(domain)
            self.domains[domain].entities[entity.name] = entity
        else:
            self.entities[entity.name] = entity
        
        # Update synonym mappings
        for synonym in entity.synonyms:
            self.entity_synonyms[synonym.lower()] = entity.name
        
        # Handle plural form
        if entity.plural_form:
            self.entity_synonyms[entity.plural_form.lower()] = entity.name
    
    def add_verb(self, verb: UserVerb, domain: Optional[str] = None):
        """Add a user-defined verb."""
        # Add to appropriate dictionary
        if domain:
            if domain not in self.domains:
                self.domains[domain] = DomainVocabulary(domain)
            self.domains[domain].verbs[verb.verb] = verb
        else:
            self.verbs[verb.verb] = verb
        
        # Update synonym mappings
        for synonym in verb.synonyms:
            self.verb_synonyms[synonym.lower()] = verb.verb
        
        # Handle past tense
        if verb.past_tense:
            self.verb_synonyms[verb.past_tense.lower()] = verb.verb
    
    def add_pattern(self, pattern: UserPattern, domain: Optional[str] = None):
        """Add a user-defined pattern."""
        if domain:
            if domain not in self.domains:
                self.domains[domain] = DomainVocabulary(domain)
            self.domains[domain].patterns[pattern.name] = pattern
        else:
            self.patterns[pattern.name] = pattern
    
    def add_abbreviation(self, abbrev: str, expansion: str, domain: Optional[str] = None):
        """Add an abbreviation expansion."""
        if domain:
            if domain not in self.domains:
                self.domains[domain] = DomainVocabulary(domain)
            self.domains[domain].abbreviations[abbrev] = expansion
        else:
            self.abbreviations[abbrev] = expansion
    
    def load_from_file(self, filepath: Union[str, Path]) -> bool:
        """Load dictionary from a file (JSON, YAML, or CSV)."""
        filepath = Path(filepath)
        
        if not filepath.exists():
            self.logger.error(f"File not found: {filepath}")
            return False
        
        try:
            suffix = filepath.suffix.lower()
            
            if suffix == '.json':
                return self._load_json(filepath)
            elif suffix in ['.yaml', '.yml']:
                return self._load_yaml(filepath)
            elif suffix == '.csv':
                return self._load_csv(filepath)
            else:
                self.logger.error(f"Unsupported file format: {suffix}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading {filepath}: {e}")
            return False
    
    def _load_json(self, filepath: Path) -> bool:
        """Load from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self._process_dictionary_data(data)
    
    def _load_yaml(self, filepath: Path) -> bool:
        """Load from YAML file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._process_dictionary_data(data)
    
    def _load_csv(self, filepath: Path) -> bool:
        """Load from CSV file."""
        # Determine type from filename
        if 'entit' in filepath.name.lower():
            return self._load_entities_csv(filepath)
        elif 'verb' in filepath.name.lower():
            return self._load_verbs_csv(filepath)
        else:
            self.logger.warning(f"Cannot determine CSV type from filename: {filepath.name}")
            return False
    
    def _load_entities_csv(self, filepath: Path) -> bool:
        """Load entities from CSV."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                entity = UserEntity(
                    name=row['name'],
                    category=row.get('category', 'object'),
                    plural_form=row.get('plural', None),
                    properties=row.get('properties', '').split('|') if row.get('properties') else [],
                    synonyms=row.get('synonyms', '').split('|') if row.get('synonyms') else [],
                    typical_verbs=row.get('verbs', '').split('|') if row.get('verbs') else []
                )
                self.add_entity(entity)
        return True
    
    def _load_verbs_csv(self, filepath: Path) -> bool:
        """Load verbs from CSV."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                verb = UserVerb(
                    verb=row['verb'],
                    past_tense=row.get('past_tense', None),
                    synonyms=row.get('synonyms', '').split('|') if row.get('synonyms') else [],
                    typical_subjects=row.get('subjects', '').split('|') if row.get('subjects') else [],
                    typical_objects=row.get('objects', '').split('|') if row.get('objects') else []
                )
                self.add_verb(verb)
        return True
    
    def _process_dictionary_data(self, data: Dict[str, Any]) -> bool:
        """Process dictionary data from JSON/YAML."""
        # Check if it's a domain vocabulary
        if 'domain' in data:
            domain = data['domain']
            vocab = DomainVocabulary(domain)
            
            # Process entities
            for name, entity_data in data.get('entities', {}).items():
                entity = UserEntity(name=name, **entity_data)
                vocab.entities[name] = entity
            
            # Process verbs
            for verb_name, verb_data in data.get('verbs', {}).items():
                verb = UserVerb(verb=verb_name, **verb_data)
                vocab.verbs[verb_name] = verb
            
            # Process patterns
            for pattern_name, pattern_data in data.get('patterns', {}).items():
                pattern = UserPattern(name=pattern_name, **pattern_data)
                vocab.patterns[pattern_name] = pattern
            
            # Process abbreviations
            vocab.abbreviations = data.get('abbreviations', {})
            
            self.domains[domain] = vocab
            
        else:
            # Process as general dictionary
            # Entities
            for name, entity_data in data.get('entities', {}).items():
                if isinstance(entity_data, dict):
                    entity = UserEntity(name=name, **entity_data)
                else:
                    # Simple format: just category
                    entity = UserEntity(name=name, category=str(entity_data))
                self.add_entity(entity)
            
            # Verbs
            for verb_name, verb_data in data.get('verbs', {}).items():
                if isinstance(verb_data, dict):
                    verb = UserVerb(verb=verb_name, **verb_data)
                else:
                    # Simple format: just past tense
                    verb = UserVerb(verb=verb_name, past_tense=str(verb_data))
                self.add_verb(verb)
            
            # Patterns
            for pattern_name, pattern_data in data.get('patterns', {}).items():
                if isinstance(pattern_data, dict):
                    pattern = UserPattern(name=pattern_name, **pattern_data)
                else:
                    # Simple format: pattern string
                    pattern = UserPattern(name=pattern_name, pattern=str(pattern_data), replacement="")
                self.add_pattern(pattern)
            
            # Abbreviations
            self.abbreviations.update(data.get('abbreviations', {}))
        
        return True
    
    def save_to_file(self, filepath: Union[str, Path], domain: Optional[str] = None):
        """Save dictionary to file."""
        filepath = Path(filepath)
        suffix = filepath.suffix.lower()
        
        if domain and domain in self.domains:
            data = self.domains[domain].to_dict()
        else:
            data = {
                "entities": {k: v.to_dict() for k, v in self.entities.items()},
                "verbs": {k: v.to_dict() for k, v in self.verbs.items()},
                "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
                "abbreviations": self.abbreviations
            }
        
        if suffix == '.json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        elif suffix in ['.yaml', '.yml']:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        else:
            raise ValueError(f"Unsupported output format: {suffix}")
    
    def lookup_entity(self, word: str) -> Optional[UserEntity]:
        """Look up an entity by name or synonym."""
        word_lower = word.lower()
        
        # Direct lookup
        if word in self.entities:
            return self.entities[word]
        
        # Synonym lookup
        if word_lower in self.entity_synonyms:
            canonical = self.entity_synonyms[word_lower]
            return self.entities.get(canonical)
        
        # Check domains
        for domain in self.domains.values():
            if word in domain.entities:
                return domain.entities[word]
        
        return None
    
    def lookup_verb(self, word: str) -> Optional[UserVerb]:
        """Look up a verb by name or synonym."""
        word_lower = word.lower()
        
        # Direct lookup
        if word in self.verbs:
            return self.verbs[word]
        
        # Synonym lookup
        if word_lower in self.verb_synonyms:
            canonical = self.verb_synonyms[word_lower]
            return self.verbs.get(canonical)
        
        # Check domains
        for domain in self.domains.values():
            if word in domain.verbs:
                return domain.verbs[word]
        
        return None
    
    def expand_abbreviation(self, abbrev: str) -> str:
        """Expand an abbreviation."""
        # Check global abbreviations
        if abbrev in self.abbreviations:
            return self.abbreviations[abbrev]
        
        # Check domain abbreviations
        for domain in self.domains.values():
            if abbrev in domain.abbreviations:
                return domain.abbreviations[abbrev]
        
        return abbrev  # Return original if not found


# Example dictionary files:

def create_example_dictionaries():
    """Create example dictionary files for users."""
    examples_dir = Path("example_dictionaries")
    examples_dir.mkdir(exist_ok=True)
    
    # Example 1: Healthcare domain (YAML)
    healthcare_dict = {
        "domain": "healthcare",
        "entities": {
            "patient": {
                "category": "person",
                "properties": ["age", "medical_history", "insurance_status"],
                "synonyms": ["client", "individual"],
                "typical_verbs": ["receives", "undergoes", "consents", "reports"]
            },
            "physician": {
                "category": "person", 
                "synonyms": ["doctor", "practitioner", "provider"],
                "typical_verbs": ["diagnoses", "prescribes", "treats", "refers"]
            },
            "medication": {
                "category": "object",
                "properties": ["dosage", "frequency", "contraindications"],
                "synonyms": ["drug", "medicine", "prescription"],
                "plural_form": "medications"
            }
        },
        "verbs": {
            "prescribes": {
                "past_tense": "prescribed",
                "typical_subjects": ["physician", "doctor"],
                "typical_objects": ["medication", "treatment"]
            },
            "diagnoses": {
                "past_tense": "diagnosed",
                "synonyms": ["identifies", "determines"],
                "typical_subjects": ["physician"],
                "typical_objects": ["condition", "disease"]
            }
        },
        "patterns": {
            "dosage_pattern": {
                "pattern": r"(\d+)\s*mg\s+(?:every|each)\s+(\d+)\s+hours?",
                "replacement": "dosage(\\1mg, \\2h)",
                "examples": ["10mg every 4 hours", "5 mg each 12 hours"]
            }
        },
        "abbreviations": {
            "BP": "blood pressure",
            "HR": "heart rate",
            "PRN": "as needed",
            "BID": "twice daily"
        }
    }
    
    with open(examples_dir / "healthcare.yaml", 'w') as f:
        yaml.dump(healthcare_dict, f, default_flow_style=False)
    
    # Example 2: Simple entities CSV
    entities_csv = """name,category,plural,synonyms,properties,verbs
employee,person,employees,worker|staff member,employee_id|department|salary,works|manages|reports
department,organization,departments,division|unit,name|budget|head_count,contains|manages
project,object,projects,task|initiative,name|deadline|budget,requires|produces|delivers
"""
    
    with open(examples_dir / "entities.csv", 'w') as f:
        f.write(entities_csv)
    
    # Example 3: Finance domain (JSON)
    finance_dict = {
        "domain": "finance",
        "entities": {
            "account": {
                "category": "object",
                "properties": ["balance", "account_number", "status"],
                "typical_verbs": ["holds", "transfers", "receives"]
            },
            "transaction": {
                "category": "event",
                "properties": ["amount", "date", "type"],
                "synonyms": ["transfer", "payment"]
            }
        },
        "verbs": {
            "transfers": {
                "past_tense": "transferred",
                "typical_subjects": ["account", "user"],
                "typical_objects": ["money", "funds"]
            }
        },
        "abbreviations": {
            "APR": "annual percentage rate",
            "ATM": "automated teller machine",
            "ROI": "return on investment"
        }
    }
    
    with open(examples_dir / "finance.json", 'w') as f:
        json.dump(finance_dict, f, indent=2)
    
    print(f"Example dictionaries created in {examples_dir}")


if __name__ == "__main__":
    # Create examples
    create_example_dictionaries()
    
    # Test the dictionary system
    dict_sys = UserDictionary()
    
    # Add a custom entity
    dict_sys.add_entity(UserEntity(
        name="robot",
        category="system",
        plural_form="robots",
        properties=["model", "capabilities"],
        synonyms=["bot", "automaton"],
        typical_verbs=["performs", "executes", "processes"]
    ))
    
    # Test lookup
    robot = dict_sys.lookup_entity("bot")
    print(f"Found entity: {robot.name if robot else 'Not found'}")
    
    # Save custom dictionary
    dict_sys.save_to_file("custom_dictionary.yaml")