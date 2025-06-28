print("Attempting to import the FastAPI app...")
try:
    from backend.tau_translator_server import app
    print("FastAPI app imported successfully.")
except Exception as e:
    print(f"An exception occurred during import: {e}")
    import traceback
    traceback.print_exc()
