"""
Defines the core domain models for the vocabulary system, such as EntityType and FieldDefinition.
"""

from typing import Optional

class FieldDefinition:
    """
    Represents the definition of a single field within an EntityType.
    """
    def __init__(self, name: str, field_data: dict):
        """
        Initialize a field definition from its data.
        
        Args:
            name: The field name
            field_data: Dictionary containing field properties
        """
        self.name = name
        self.type = field_data.get("type", "string")
        self.required = field_data.get("required", False)
        self.description = field_data.get("description", "")
        self.default = field_data.get("default")
        self.constraints = field_data.get("constraints", {})
        self.examples = field_data.get("examples", [])
        
    def __repr__(self):
        return f"FieldDefinition(name={self.name}, type={self.type}, required={self.required})"

class EntityType:
    """
    Represents a type of entity in the domain, loaded from vocabulary definitions.
    """
    def __init__(self, name: str, definition_data: dict):
        """
        Initializes an EntityType from its name and definition dictionary.

        Args:
            name: The name of the entity type (e.g., "USER").
            definition_data: A dictionary containing the entity's definition,
                             typically loaded from a JSON file.
        """
        self.name: str = name
        self.description: Optional[str] = definition_data.get("description")
        self.schema_version: Optional[str] = definition_data.get("schema_version")
        
        # Parse fields data into FieldDefinition objects
        self.raw_fields_data: dict = definition_data.get("fields", {})
        self.fields: dict[str, FieldDefinition] = {}
        
        # Parse each field definition
        for field_name, field_data in self.raw_fields_data.items():
            self.fields[field_name] = FieldDefinition(field_name, field_data)

    def __repr__(self) -> str:
        return f"<EntityType(name='{self.name}')>"

