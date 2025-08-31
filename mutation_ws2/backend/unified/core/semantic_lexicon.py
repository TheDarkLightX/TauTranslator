"""
Semantic Lexicon for Complex English to Tau Translation
Provides rich semantic knowledge for handling complex natural language.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum


class EntityCategory(Enum):
    """Categories of entities for semantic reasoning."""
    PERSON = "person"
    OBJECT = "object"
    LOCATION = "location"
    TIME = "time"
    EVENT = "event"
    ABSTRACT = "abstract"
    ORGANIZATION = "organization"
    SYSTEM = "system"
    DOCUMENT = "document"
    QUANTITY = "quantity"


class RelationType(Enum):
    """Types of relationships between entities."""
    OWNERSHIP = "owns"
    LOCATION = "located_at"
    TEMPORAL = "occurs_at"
    PARTICIPATION = "participates_in"
    MEMBERSHIP = "member_of"
    CREATION = "creates"
    MODIFICATION = "modifies"
    CAUSATION = "causes"
    REQUIREMENT = "requires"
    PERMISSION = "permits"


@dataclass
class SemanticEntity:
    """Rich semantic information about an entity type."""
    name: str
    category: EntityCategory
    properties: Set[str] = field(default_factory=set)
    typical_actions: Set[str] = field(default_factory=set)
    typical_relations: Dict[RelationType, Set[str]] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    plural_form: Optional[str] = None
    singular_form: Optional[str] = None


@dataclass
class SemanticAction:
    """Semantic information about actions/verbs."""
    verb: str
    agent_type: Optional[EntityCategory] = None
    patient_type: Optional[EntityCategory] = None
    result_type: Optional[EntityCategory] = None
    preconditions: List[str] = field(default_factory=list)
    effects: List[str] = field(default_factory=list)
    synonyms: Set[str] = field(default_factory=set)


class SemanticLexicon:
    """
    Comprehensive semantic lexicon for natural language understanding.
    Provides domain knowledge for complex sentence parsing.
    """
    
    def __init__(self, lexicon_path: Optional[Any] = None):
        self.lexicon_path = lexicon_path
        self._initialize_entity_lexicon()
        self._initialize_action_lexicon()
        self._initialize_property_lexicon()
        self._initialize_relation_mappings()
        self._initialize_domain_patterns()
    
    def _initialize_entity_lexicon(self):
        """Initialize entity semantic knowledge."""
        self.entities = {
            # People
            "person": SemanticEntity(
                name="person",
                category=EntityCategory.PERSON,
                properties={"age", "name", "gender", "occupation"},
                typical_actions={"owns", "drives", "pays", "works", "lives", "buys"},
                typical_relations={
                    RelationType.OWNERSHIP: {"car", "house", "phone", "account"},
                    RelationType.MEMBERSHIP: {"organization", "company", "group"},
                    RelationType.LOCATION: {"city", "country", "address"}
                },
                plural_form="people"
            ),
            "customer": SemanticEntity(
                name="customer",
                category=EntityCategory.PERSON,
                properties={"customer_id", "loyalty_status", "purchase_history"},
                typical_actions={"purchases", "orders", "returns", "complains", "pays"},
                typical_relations={
                    RelationType.OWNERSHIP: {"account", "order", "subscription"},
                    RelationType.PARTICIPATION: {"transaction", "purchase", "order"}
                },
                plural_form="customers"
            ),
            "employee": SemanticEntity(
                name="employee",
                category=EntityCategory.PERSON,
                properties={"employee_id", "department", "salary", "tenure"},
                typical_actions={"works", "manages", "reports", "completes", "submits"},
                typical_relations={
                    RelationType.MEMBERSHIP: {"department", "team", "company"},
                    RelationType.CREATION: {"report", "document", "project"}
                },
                plural_form="employees"
            ),
            
            # Objects
            "car": SemanticEntity(
                name="car",
                category=EntityCategory.OBJECT,
                properties={"color", "make", "model", "year", "license_plate"},
                typical_actions={"drives", "parks", "starts", "stops"},
                typical_relations={
                    RelationType.OWNERSHIP: {"person", "company"},
                    RelationType.REQUIREMENT: {"insurance", "registration", "fuel"}
                },
                plural_form="cars"
            ),
            "house": SemanticEntity(
                name="house",
                category=EntityCategory.OBJECT,
                properties={"address", "size", "rooms", "value"},
                typical_actions={"shelters", "contains"},
                typical_relations={
                    RelationType.OWNERSHIP: {"person", "family"},
                    RelationType.LOCATION: {"city", "neighborhood"},
                    RelationType.REQUIREMENT: {"insurance", "maintenance", "taxes"}
                },
                plural_form="houses"
            ),
            
            # Systems
            "system": SemanticEntity(
                name="system",
                category=EntityCategory.SYSTEM,
                properties={"status", "configuration", "version"},
                typical_actions={"processes", "validates", "returns", "blocks", "allows"},
                typical_relations={
                    RelationType.MODIFICATION: {"data", "request", "record"},
                    RelationType.CREATION: {"log", "error", "response"}
                },
                plural_form="systems"
            ),
            
            # Documents/Data
            "order": SemanticEntity(
                name="order",
                category=EntityCategory.DOCUMENT,
                properties={"order_id", "total", "status", "date"},
                typical_actions={"contains", "includes"},
                typical_relations={
                    RelationType.OWNERSHIP: {"customer"},
                    RelationType.PARTICIPATION: {"transaction", "shipment"}
                },
                plural_form="orders"
            ),
            "payment": SemanticEntity(
                name="payment",
                category=EntityCategory.EVENT,
                properties={"amount", "method", "status", "date"},
                typical_actions={"completes", "fails", "processes"},
                typical_relations={
                    RelationType.PARTICIPATION: {"customer", "transaction"},
                    RelationType.CAUSATION: {"discount", "receipt"}
                },
                plural_form="payments"
            ),
        }
        
        # Add shortcuts for common variations
        self.entity_variations = {
            "people": "person",
            "client": "customer",
            "clients": "customer",
            "user": "customer",
            "users": "customer",
            "worker": "employee",
            "workers": "employee",
            "staff": "employee",
            "vehicle": "car",
            "vehicles": "car",
            "home": "house",
            "homes": "house",
            "property": "house",
            "properties": "house"
        }
    
    def _initialize_action_lexicon(self):
        """Initialize action/verb semantic knowledge."""
        self.actions = {
            "owns": SemanticAction(
                verb="owns",
                agent_type=EntityCategory.PERSON,
                patient_type=EntityCategory.OBJECT,
                synonyms={"has", "possesses", "holds"}
            ),
            "purchases": SemanticAction(
                verb="purchases",
                agent_type=EntityCategory.PERSON,
                patient_type=EntityCategory.OBJECT,
                result_type=EntityCategory.DOCUMENT,
                effects=["creates order", "reduces balance", "increases purchase_history"],
                synonyms={"buys", "orders", "acquires"}
            ),
            "pays": SemanticAction(
                verb="pays",
                agent_type=EntityCategory.PERSON,
                result_type=EntityCategory.EVENT,
                effects=["creates payment", "updates balance"],
                synonyms={"remits", "settles", "compensates"}
            ),
            "drives": SemanticAction(
                verb="drives",
                agent_type=EntityCategory.PERSON,
                patient_type=EntityCategory.OBJECT,
                preconditions=["has license", "car is operational"],
                synonyms={"operates", "pilots"}
            ),
            "receives": SemanticAction(
                verb="receives",
                agent_type=EntityCategory.PERSON,
                synonyms={"gets", "obtains", "acquires", "is given"}
            ),
            "blocks": SemanticAction(
                verb="blocks",
                agent_type=EntityCategory.SYSTEM,
                effects=["prevents access", "denies request"],
                synonyms={"prevents", "denies", "restricts", "prohibits"}
            )
        }
    
    def _initialize_property_lexicon(self):
        """Initialize property/adjective semantic knowledge."""
        self.properties = {
            # Colors
            "red": {"category": "color", "applies_to": {"car", "house", "object"}},
            "blue": {"category": "color", "applies_to": {"car", "house", "object"}},
            "green": {"category": "color", "applies_to": {"car", "house", "object"}},
            
            # Sizes
            "large": {"category": "size", "comparative": "larger", "superlative": "largest"},
            "small": {"category": "size", "comparative": "smaller", "superlative": "smallest"},
            
            # Status
            "active": {"category": "status", "opposite": "inactive"},
            "valid": {"category": "status", "opposite": "invalid"},
            "outstanding": {"category": "status", "implies": "unpaid"},
            
            # Quantities
            "positive": {"category": "quantity", "constraint": "> 0"},
            "negative": {"category": "quantity", "constraint": "< 0"},
            "high": {"category": "quantity", "comparative": "higher", "constraint": "> threshold"},
            "low": {"category": "quantity", "comparative": "lower", "constraint": "< threshold"}
        }
    
    def _initialize_relation_mappings(self):
        """Initialize mappings for complex relationships."""
        # Maps phrases to formal relations
        self.relation_patterns = {
            "who owns": "ownership_relation",
            "that belongs to": "ownership_relation",
            "located in": "location_relation",
            "member of": "membership_relation",
            "works for": "employment_relation",
            "responsible for": "responsibility_relation",
            "totaling more than": "sum_exceeds",
            "in the last": "time_window",
            "per minute": "rate_per_time",
            "has no": "not exists",
            "must have": "requires",
            "receives a": "obtains"
        }
    
    def _initialize_domain_patterns(self):
        """Initialize domain-specific patterns."""
        self.domain_patterns = {
            "business": {
                "discount_rule": {
                    "pattern": r"receives?\s+a?\s*(\d+)%?\s*discount",
                    "extraction": ["discount_percentage"]
                },
                "purchase_threshold": {
                    "pattern": r"purchases?\s+(?:totaling|exceeding|over)\s+\$?(\d+)",
                    "extraction": ["amount_threshold"]
                },
                "time_window": {
                    "pattern": r"in\s+the\s+last\s+(\d+)\s+(days?|months?|years?)",
                    "extraction": ["duration", "time_unit"]
                }
            },
            "system": {
                "rate_limit": {
                    "pattern": r"(\d+)\s+requests?\s+per\s+(second|minute|hour)",
                    "extraction": ["request_count", "time_unit"]
                },
                "blocking_duration": {
                    "pattern": r"block\s+(?:for|during)\s+(\d+)\s+(seconds?|minutes?|hours?)",
                    "extraction": ["duration", "time_unit"]
                }
            }
        }
    
    def get_entity_info(self, entity_name: str) -> Optional[SemanticEntity]:
        """Get semantic information about an entity."""
        # Check variations first
        entity_name = entity_name.lower()
        if entity_name in self.entity_variations:
            entity_name = self.entity_variations[entity_name]
        
        return self.entities.get(entity_name)
    
    def get_action_info(self, verb: str) -> Optional[SemanticAction]:
        """Get semantic information about an action."""
        verb = verb.lower()
        
        # Direct lookup
        if verb in self.actions:
            return self.actions[verb]
        
        # Check synonyms
        for action_name, action in self.actions.items():
            if verb in action.synonyms:
                return action
        
        return None
    
    def infer_entity_type(self, context: List[str]) -> Optional[EntityCategory]:
        """Infer entity type from context clues."""
        context_str = " ".join(context).lower()
        
        # Check for type indicators
        type_indicators = {
            EntityCategory.PERSON: ["who", "person", "people", "someone", "customer", "employee"],
            EntityCategory.OBJECT: ["that", "which", "something", "car", "house", "product"],
            EntityCategory.LOCATION: ["where", "place", "location", "city", "country"],
            EntityCategory.TIME: ["when", "time", "date", "period", "duration"],
            EntityCategory.SYSTEM: ["system", "application", "service", "platform"]
        }
        
        for category, indicators in type_indicators.items():
            if any(indicator in context_str for indicator in indicators):
                return category
        
        return None
    
    def get_typical_relations(self, entity1: str, entity2: str) -> List[RelationType]:
        """Get typical relations between two entity types."""
        entity1_info = self.get_entity_info(entity1)
        entity2_info = self.get_entity_info(entity2)
        
        if not entity1_info:
            return []
        
        relations = []
        for rel_type, related_entities in entity1_info.typical_relations.items():
            if entity2 in related_entities or (entity2_info and entity2_info.name in related_entities):
                relations.append(rel_type)
        
        return relations
    
    def extract_domain_patterns(self, text: str, domain: str = "business") -> Dict[str, Any]:
        """Extract domain-specific patterns from text."""
        extracted = {}
        
        if domain in self.domain_patterns:
            import re
            for pattern_name, pattern_info in self.domain_patterns[domain].items():
                match = re.search(pattern_info["pattern"], text, re.IGNORECASE)
                if match:
                    extracted[pattern_name] = {}
                    for i, field in enumerate(pattern_info["extraction"], 1):
                        extracted[pattern_name][field] = match.group(i)
        
        return extracted
    
    def classify_entity(self, entity: str) -> EntityCategory:
        """Classify entity type."""
        entity_info = self.get_entity_info(entity)
        if entity_info:
            return entity_info.category
        
        # Default classification based on common patterns
        entity_lower = entity.lower()
        if entity_lower in ['person', 'people', 'customer', 'employee', 'user']:
            return EntityCategory.PERSON
        elif entity_lower in ['car', 'house', 'product', 'item', 'object']:
            return EntityCategory.OBJECT
        elif entity_lower in ['system', 'application', 'service']:
            return EntityCategory.SYSTEM
        else:
            return EntityCategory.ABSTRACT
    
    def extract_relations(self, text: str) -> List[Tuple[str, RelationType, str]]:
        """Extract semantic relations from text."""
        relations = []
        import re
        
        # Simple relation patterns
        ownership_pattern = r'(\w+)\s+(?:owns?|has|possesses)\s+(\w+)'
        causal_pattern = r'(\w+)\s+(?:causes?|leads?\s+to)\s+(\w+)'
        temporal_pattern = r'(\w+)\s+(?:occurs?\s+at|happens?\s+during)\s+(\w+)'
        
        for pattern, rel_type in [
            (ownership_pattern, RelationType.OWNERSHIP),
            (causal_pattern, RelationType.CAUSATION),
            (temporal_pattern, RelationType.TEMPORAL)
        ]:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                relations.append((match.group(1), rel_type, match.group(2)))
        
        return relations
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract entities from text."""
        import re
        # Simple entity extraction - nouns and proper nouns
        words = re.findall(r'\b[A-Z][a-z]+\b|\b(?:person|people|customer|car|house|system)\b', text, re.IGNORECASE)
        return list(set(words))
    
    def add_entity_properties(self, entity: str, properties: Set[str]):
        """Add properties to an entity."""
        if entity in self.entities:
            self.entities[entity].properties.update(properties)
        else:
            # Create new entity
            self.entities[entity] = SemanticEntity(
                name=entity,
                category=EntityCategory.ABSTRACT,
                properties=properties
            )


# Singleton instance
_lexicon = None

def get_semantic_lexicon() -> SemanticLexicon:
    """Get the singleton semantic lexicon instance."""
    global _lexicon
    if _lexicon is None:
        _lexicon = SemanticLexicon()
    return _lexicon