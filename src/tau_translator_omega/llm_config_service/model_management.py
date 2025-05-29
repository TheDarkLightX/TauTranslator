import os
import shutil
from pathlib import Path
import psutil
from huggingface_hub import snapshot_download, HfApi, hf_hub_url
from huggingface_hub.utils import GatedRepoError, RepositoryNotFoundError

# --- Configuration ---
MODELS_BASE_DIR = Path("~/TauTranslator/models")

# Placeholder for Gemma 3 models - replace with actual IDs and realistic requirements
# Gemma 3 model IDs are not yet finalized in this example, using plausible names.
# Resource requirements are estimates and should be verified.
GEMMA_MODELS_DEFINITIONS = [
    {
        "id": "google/gemma-3-2b-it", # Example ID
        "name": "Gemma-3 2B (Instruct)",
        "estimated_ram_gb_min": 8,    # Minimum RAM to load
        "estimated_ram_gb_load": 12,  # RAM for comfortable loading and initial inference
        "estimated_disk_gb": 5,       # Approximate disk space for model files
        "notes": "Smaller, faster, good for simpler tasks."
    },
    {
        "id": "google/gemma-3-9b-it", # Example ID
        "name": "Gemma-3 9B (Instruct)",
        "estimated_ram_gb_min": 24,
        "estimated_ram_gb_load": 32,
        "estimated_disk_gb": 20,
        "notes": "Larger, more capable, for complex tasks."
    },
    # Add other Gemma 3 variants as they become known/relevant
]

# Ensure the base models directory exists
MODELS_BASE_DIR.mkdir(parents=True, exist_ok=True)

# --- System Resource Functions ---

def get_system_resources():
    """Gets available system resources relevant for model management."""
    virtual_mem = psutil.virtual_memory()
    disk_usage = psutil.disk_usage(str(MODELS_BASE_DIR))
    return {
        "total_ram_gb": round(virtual_mem.total / (1024**3), 2),
        "available_ram_gb": round(virtual_mem.available / (1024**3), 2),
        "models_dir_total_disk_gb": round(disk_usage.total / (1024**3), 2),
        "models_dir_available_disk_gb": round(disk_usage.free / (1024**3), 2),
    }

# --- Model Definition and Status Functions ---

def get_gemma_model_definitions_with_status():
    """Returns Gemma model definitions along with their download status."""
    definitions_with_status = []
    for model_def in GEMMA_MODELS_DEFINITIONS:
        model_id = model_def["id"]
        model_path = MODELS_BASE_DIR / model_id.replace("/", "_") # Store as google_gemma-3-2b-it
        status = "downloaded" if model_path.exists() and any(model_path.iterdir()) else "not_downloaded"
        definitions_with_status.append({
            **model_def,
            "local_path": str(model_path),
            "status": status
        })
    return definitions_with_status

def get_model_info_by_id(model_id_to_find: str):
    """Gets a specific model's definition and status by its Hugging Face ID."""
    for model_info in get_gemma_model_definitions_with_status():
        if model_info["id"] == model_id_to_find:
            return model_info
    return None

# --- Model Management Functions ---

def download_gemma_model(model_id: str, hf_token: Optional[str] = None):
    """Downloads a specified Gemma model from Hugging Face Hub."""
    model_info = get_model_info_by_id(model_id)
    if not model_info:
        return {"error": f"Model ID {model_id} not found in definitions."}

    local_model_path = Path(model_info["local_path"])
    if local_model_path.exists() and any(local_model_path.iterdir()):
        return {"status": "already_downloaded", "path": str(local_model_path)}

    local_model_path.mkdir(parents=True, exist_ok=True)

    try:
        snapshot_download(
            repo_id=model_id,
            local_dir=str(local_model_path),
            local_dir_use_symlinks=False, # Recommended to be False for wider compatibility
            token=hf_token, # Pass token if model requires authentication (e.g. gated models)
            # resume_download=True, # Enable if desired
            # ignore_patterns=["*.safetensors"], # Example: if you only want pytorch .bin files
        )
        return {"status": "download_successful", "path": str(local_model_path)}
    except GatedRepoError:
        shutil.rmtree(local_model_path) # Clean up partial download directory
        return {"error": f"Access to model {model_id} is gated. A Hugging Face token with access is required."}
    except RepositoryNotFoundError:
        shutil.rmtree(local_model_path)
        return {"error": f"Model repository {model_id} not found on Hugging Face Hub."}
    except Exception as e:
        shutil.rmtree(local_model_path) # Clean up on any other error
        return {"error": f"Failed to download model {model_id}: {str(e)}"}

def delete_gemma_model(model_id: str):
    """Deletes a downloaded Gemma model from local storage."""
    model_info = get_model_info_by_id(model_id)
    if not model_info:
        return {"error": f"Model ID {model_id} not found in definitions."}

    local_model_path = Path(model_info["local_path"])

    if not local_model_path.exists():
        return {"status": "not_found", "message": "Model was not downloaded or already deleted."}

    try:
        shutil.rmtree(local_model_path)
        return {"status": "deletion_successful"}
    except Exception as e:
        return {"error": f"Failed to delete model {model_id} directory: {str(e)}"}


# --- LMQL and Guidance Placeholder Functions ---
# These are very basic placeholders. Actual implementation will be more complex.

def load_model_with_guidance(model_id: str):
    """Placeholder for loading a model with the Guidance library."""
    model_info = get_model_info_by_id(model_id)
    if not model_info or model_info["status"] != "downloaded":
        return {"error": "Model not downloaded or not found."}
    
    # Actual Guidance loading logic would go here, e.g.:
    # import guidance
    # guidance.llm = guidance.llms.Transformers(model_info["local_path"], device=0) # Example
    # return {"status": "Model ready for Guidance", "guidance_llm_instance": guidance.llm}
    return {"status": "placeholder_guidance_load_ok", "model_path": model_info["local_path"]}

def run_lmql_query(query: str, model_id: str):
    """Placeholder for running an LMQL query."""
    model_info = get_model_info_by_id(model_id)
    if not model_info or model_info["status"] != "downloaded":
        return {"error": "Model not downloaded or not found for LMQL."}

    # Actual LMQL execution logic would go here, e.g.:
    # import lmql
    # output = await lmql.run(query, model=model_info["local_path"]) # Example
    # return {"status": "lmql_query_executed", "output": output}
    return {"status": "placeholder_lmql_run_ok", "model_path": model_info["local_path"], "query": query}


if __name__ == '__main__':
    # Example usage (for direct testing of this module)
    print("System Resources:", get_system_resources())
    print("\nGemma Models:", get_gemma_model_definitions_with_status())

    # Test download (replace with a small, public model for quick testing if needed)
    # test_model_id_to_download = "google/gemma-3-2b-it" 
    # print(f"\nAttempting to download {test_model_id_to_download}...")
    # download_result = download_gemma_model(test_model_id_to_download)
    # print("Download result:", download_result)

    # print("\nUpdated Gemma Models List:", get_gemma_model_definitions_with_status())

    # Test deletion
    # if download_result.get("status") == "download_successful" or download_result.get("status") == "already_downloaded":
    #     print(f"\nAttempting to delete {test_model_id_to_download}...")
    #     delete_result = delete_gemma_model(test_model_id_to_download)
    #     print("Deletion result:", delete_result)
    #     print("\nFinal Gemma Models List:", get_gemma_model_definitions_with_status())

    # print("\nGuidance Load Placeholder:", load_model_with_guidance(test_model_id_to_download))
    # print("\nLMQL Run Placeholder:", run_lmql_query("SAMPLE QUERY", test_model_id_to_download))
    pass
