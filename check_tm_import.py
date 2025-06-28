import sys
from pathlib import Path

# Add project root to sys.path, similar to conftest.py
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"Current sys.path: {sys.path}")
print("Attempting to import TranslationOrchestrator from backend.unified.translators.orchestrator...")
try:
    from backend.unified.translators.orchestrator import TranslationOrchestrator
    print("Successfully imported TranslationOrchestrator.")
    print(f"TranslationOrchestrator type: {type(TranslationOrchestrator)}")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An unexpected error occurred during import or instantiation: {e}")
    import traceback
    traceback.print_exc()
print("Script finished.")
