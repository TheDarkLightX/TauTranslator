from typing import List, Optional, Dict
from .models import LLMService, LLMServiceCreate, LLMServiceUpdate
import uuid

# In-memory storage for LLM services
# In a production scenario, this would be replaced with a database.
db_services: Dict[str, LLMService] = {}

def get_llm_services() -> List[LLMService]:
    """Retrieve all LLM services."""
    return list(db_services.values())

def get_llm_service(service_id: str) -> Optional[LLMService]:
    """Retrieve a single LLM service by its ID."""
    return db_services.get(service_id)

def create_llm_service(service_create: LLMServiceCreate) -> LLMService:
    """Create a new LLM service."""
    service_id = str(uuid.uuid4())
    # If this is the first service being added, make it default.
    # Otherwise, new services are not default unless explicitly set.
    is_default = not bool(db_services) 
    
    new_service = LLMService(
        id=service_id,
        **service_create.model_dump(), # Pydantic v2
        isDefault=is_default
    )
    if new_service.isDefault:
        # Ensure no other service is marked as default
        for s_id in db_services:
            if db_services[s_id].isDefault:
                db_services[s_id].isDefault = False
                break # There should only be one default

    db_services[service_id] = new_service
    return new_service

def update_llm_service(service_id: str, service_update: LLMServiceUpdate) -> Optional[LLMService]:
    """Update an existing LLM service."""
    existing_service = db_services.get(service_id)
    if not existing_service:
        return None

    update_data = service_update.model_dump(exclude_unset=True) # Pydantic v2
    for key, value in update_data.items():
        setattr(existing_service, key, value)
    
    db_services[service_id] = existing_service
    return existing_service

def delete_llm_service(service_id: str) -> Optional[LLMService]:
    """Delete an LLM service."""
    deleted_service = db_services.pop(service_id, None)
    if deleted_service and deleted_service.isDefault and db_services:
        # If the deleted service was default, try to set another one as default
        # (e.g., the first one in the list, or based on some other logic)
        # For simplicity, let's make the first available service default.
        new_default_id = next(iter(db_services))
        db_services[new_default_id].isDefault = True
    return deleted_service

def set_default_llm_service(service_id: str) -> Optional[LLMService]:
    """Set a specific LLM service as the default."""
    target_service = db_services.get(service_id)
    if not target_service:
        return None

    for s_id in db_services:
        db_services[s_id].isDefault = (s_id == service_id)
    
    return target_service
