import pytest
import json
from pathlib import Path

from tau_translator_omega.vocabulary.domain_model import EntityType #, FieldDefinition
# from tau_translator_omega.vocabulary.exceptions import FieldNotFoundError

# FieldDefinition will be imported later when tests for it are added

@pytest.fixture
def sample_entity_types_data():
    p = Path(__file__).parent / "sample_entity_types.json"
    with open(p, 'r') as f:
        return json.load(f)

def test_create_entity_type_from_data(sample_entity_types_data):
    """
    Test that an EntityType object can be created from raw dictionary data.
    """
    user_data = sample_entity_types_data["USER"]
    entity_name = "USER"
    
    entity_type = EntityType(name=entity_name, definition_data=user_data)
    
    assert entity_type.name == "USER"
    assert entity_type.description == "Represents a user account."
    assert entity_type.schema_version == "1.0"
    # Check that raw fields data is stored (as per placeholder EntityType)
    assert "user_id" in entity_type.raw_fields_data 
    assert "username" in entity_type.raw_fields_data

# Next tests would involve:
# - Parsing FieldDefinition objects correctly
# - Getting a field by name (entity_type.get_field("username"))
# - Handling missing fields (raising FieldNotFoundError)
# - Validating required parts of the definition_data upon load (e.g., 'fields' must exist)
