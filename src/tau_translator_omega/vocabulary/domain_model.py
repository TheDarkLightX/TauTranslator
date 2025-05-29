"""
Defines the core domain models for the vocabulary system, such as EntityType and FieldDefinition.
"""

class FieldDefinition:
    """
    Represents the definition of a single field within an EntityType.
    Placeholder for now, will be expanded.
    """
    # TODO: Implement based on sample_entity_types.json field structure
    pass

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
        self.description: str | None = definition_data.get("description")
        self.schema_version: str | None = definition_data.get("schema_version")
        
        # For now, we'll store the raw fields data.
        # In a later step, these will be parsed into FieldDefinition objects.
        self.raw_fields_data: dict = definition_data.get("fields", {})
        self.fields: dict[str, FieldDefinition] = {}

        # TODO: Implement parsing of self.raw_fields_data into self.fields
        #       where keys are field names and values are FieldDefinition objects.

    def __repr__(self) -> str:
        return f"<EntityType(name='{self.name}')>"

