from fastapi import FastAPI, HTTPException, Body, Depends
from typing import List, Optional

from . import crud
from . import model_management as mm
from .models import (
    LLMService, LLMServiceCreate, LLMServiceUpdate,
    ModelDownloadRequest, ModelLoadRequest, LMQLQueryRequest
)

# Create a specific FastAPI instance for this service
# This helps if you have multiple FastAPI apps or want to mount this as a sub-app later.
llm_app = FastAPI(
    title="TauTranslatorOmega - LLM Configuration Service",
    description="API for managing LLM service configurations.",
    version="0.1.0"
)

# --- API Endpoints for LLM Services ---
# The prefix /api will be handled by the proxy in next.config.js for the PWA,
# and by the uvicorn command or a parent router if this app is mounted.
# For standalone running, we define routes relative to the app's root.
# The PWA will call /api/llm-services, which gets proxied to http://localhost:45311/api/llm-services
# So, the FastAPI router should listen on /api/llm-services.

API_PREFIX = "/api" # Define the prefix to be used consistently

@llm_app.get(f"{API_PREFIX}/llm-services", response_model=List[LLMService], tags=["LLM Services"])
async def read_llm_services():
    """Retrieve all configured LLM services."""
    return crud.get_llm_services()

@llm_app.post(f"{API_PREFIX}/llm-services", response_model=LLMService, status_code=201, tags=["LLM Services"])
async def create_llm_service(service: LLMServiceCreate = Body(...)):
    """Create a new LLM service configuration."""
    return crud.create_llm_service(service_create=service)

@llm_app.get(f"{API_PREFIX}/llm-services/{{service_id}}", response_model=LLMService, tags=["LLM Services"])
async def read_llm_service(service_id: str):
    """Retrieve a specific LLM service by its ID."""
    db_service = crud.get_llm_service(service_id=service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="LLM Service not found")
    return db_service

@llm_app.put(f"{API_PREFIX}/llm-services/{{service_id}}", response_model=LLMService, tags=["LLM Services"])
async def update_llm_service(service_id: str, service: LLMServiceUpdate = Body(...)):
    """Update an existing LLM service configuration."""
    updated_service = crud.update_llm_service(service_id=service_id, service_update=service)
    if updated_service is None:
        raise HTTPException(status_code=404, detail="LLM Service not found")
    return updated_service

@llm_app.delete(f"{API_PREFIX}/llm-services/{{service_id}}", response_model=LLMService, tags=["LLM Services"])
async def delete_llm_service(service_id: str):
    """Delete an LLM service configuration."""
    deleted_service = crud.delete_llm_service(service_id=service_id)
    if deleted_service is None:
        raise HTTPException(status_code=404, detail="LLM Service not found")
    return deleted_service

@llm_app.post(f"{API_PREFIX}/llm-services/{{service_id}}/set-default", response_model=LLMService, tags=["LLM Services"])
async def set_default_llm_service(service_id: str):
    """Set a specific LLM service as the default."""
    service = crud.set_default_llm_service(service_id=service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="LLM Service not found or could not be set as default")
    return service

# --- Model Management Endpoints ---

@llm_app.get(f"{API_PREFIX}/system/resources", tags=["Model Management"], summary="Get Server System Resources")
async def get_server_system_resources():
    """Retrieve server's available RAM and disk space for model storage."""
    return mm.get_system_resources()

@llm_app.get(f"{API_PREFIX}/gemma-models", tags=["Model Management"], summary="List Gemma Models")
async def list_gemma_models_with_status():
    """List available Gemma models, their requirements, and download status."""
    return mm.get_gemma_model_definitions_with_status()

@llm_app.post(f"{API_PREFIX}/gemma-models/download", tags=["Model Management"], summary="Download Gemma Model")
async def download_gemma_model_endpoint(request: ModelDownloadRequest = Body(...)):
    """Download a specified Gemma model from Hugging Face Hub."""
    # In a production app, this should be an async background task.
    # For now, it's a blocking call.
    result = mm.download_gemma_model(model_id=request.model_id, hf_token=request.hf_token)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@llm_app.delete(f"{API_PREFIX}/gemma-models/{{model_id:path}}", tags=["Model Management"], summary="Delete Gemma Model")
async def delete_gemma_model_endpoint(model_id: str):
    """Delete a downloaded Gemma model. Model ID should be the Hugging Face ID (e.g., google/gemma-3-2b-it)."""
    # The :path converter allows slashes in the model_id
    result = mm.delete_gemma_model(model_id=model_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    if result.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="Model not found or not downloaded.")
    return result

# --- Guidance and LMQL Placeholder Endpoints ---

@llm_app.post(f"{API_PREFIX}/guidance/load-model", tags=["LLM Operations"], summary="Load Model with Guidance (Placeholder)")
async def guidance_load_model(request: ModelLoadRequest = Body(...)):
    """Placeholder: Load a specified model for use with the Guidance library."""
    result = mm.load_model_with_guidance(model_id=request.model_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@llm_app.post(f"{API_PREFIX}/lmql/run-query", tags=["LLM Operations"], summary="Run LMQL Query (Placeholder)")
async def lmql_run_query(request: LMQLQueryRequest = Body(...)):
    """Placeholder: Run an LMQL query using a specified model."""
    result = mm.run_lmql_query(query=request.query, model_id=request.model_id)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# --- Health Check for this service ---
@llm_app.get(f"{API_PREFIX}/llm-config/health", tags=["LLM Service Health"])
async def health_check():
    return {"status": "healthy", "service_name": "LLM Configuration Service"}

# To run this FastAPI app directly (for development/testing this service independently):
# Use uvicorn: uvicorn tau_translator_omega.llm_config_service.main:llm_app --reload --port 45311
# Ensure your PYTHONPATH is set up correctly if running from outside the project root, or run as a module:
# python -m uvicorn tau_translator_omega.llm_config_service.main:llm_app --reload --port 45311
