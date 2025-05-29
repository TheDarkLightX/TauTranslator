from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

class LLMServiceBase(BaseModel):
    name: str = Field(..., description="User-defined name for the LLM service")
    providerType: str = Field(..., description="Type of provider, e.g., 'OpenAI API', 'OpenRouter API', 'Local Model (Ollama)', 'Local Model (Custom API)'")
    apiKey: Optional[str] = Field(None, description="API key, if required by the provider")
    modelId: Optional[str] = Field(None, description="Specific model ID, e.g., 'gpt-4-turbo', 'anthropic/claude-3-sonnet', 'gemma:7b'")
    baseUrl: Optional[str] = Field(None, description="Base URL for custom API endpoints, e.g., for local models like 'http://localhost:11434'")

class LLMServiceCreate(LLMServiceBase):
    pass

class LLMServiceUpdate(LLMServiceBase):
    name: Optional[str] = None
    providerType: Optional[str] = None
    # apiKey: Optional[str] = None # API keys are sensitive. Consider separate secure update mechanism.
    modelId: Optional[str] = None
    baseUrl: Optional[str] = None

class LLMService(LLMServiceBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier for the LLM service")
    isDefault: bool = Field(False, description="Whether this service is the default one")

    class Config:
        from_attributes = True # Pydantic v2 compatibility

# --- Models for Model Management ---

class ModelDownloadRequest(BaseModel):
    model_id: str
    hf_token: Optional[str] = None

class ModelLoadRequest(BaseModel): # Can be used for Guidance or other model loading operations
    model_id: str

class LMQLQueryRequest(BaseModel):
    model_id: str
    query: str
