# Documentation: TauTranslator Backend Server (`tau_translator_server.py`)

**File Path:** `backend/tau_translator_server.py`

## 1. Overview

The `tau_translator_server.py` script is the central nervous system of the TauTranslatorOmega application. It is a robust, production-ready backend built using the **FastAPI** web framework. Its primary role is to serve as a secure bridge between the frontend Progressive Web App (PWA) and the powerful suite of translation engines and AI provider services.

The server is designed with security, modularity, and resilience as core principles.

---

## 2. Core Architecture: `TauTranslatorBackend` Class

The `TauTranslatorBackend` class is the main service orchestrator. It encapsulates all the core business logic of the backend.

### Key Responsibilities:

-   **Dynamic Engine Loading**: Upon initialization, the class dynamically discovers and loads all available translation engines (e.g., `LMQLBidirectionalTranslator`, `TCETauTranslator`, `CNLParser`, `gemma3_translator`). This makes the system highly extensible, allowing new translation modules to be integrated with minimal code changes.
-   **Secure Storage Integration**: It manages the lifecycle of the `SecureStorage` instance, which is responsible for encrypting and persisting sensitive API keys.
-   **Translation Orchestration**: The `translate_text` method is the primary entry point for translation tasks. It intelligently routes requests to the appropriate internal translation engine or external AI provider based on the source and target languages.
-   **Authentication and Session Management**: It handles the master password authentication and manages simple session tokens to secure its endpoints.

---

## 3. Security Model

Security is a foundational aspect of the backend server.

-   **Master Password Authentication**: Access to the backend is protected by a master password. The `/api/auth` endpoint validates this password and, upon success, returns a temporary session token.
-   **Session Token**: All subsequent API calls must include this session token in the `Authorization` header. This ensures that only authenticated clients can access the server's functionality.
-   **Secure API Key Storage**: The server integrates with `secure_core.py` to provide end-to-end encryption for third-party API keys (e.g., for OpenAI, Anthropic). Keys are never stored in plaintext.

---

## 4. API Contract: Pydantic Models

The API's data structures are rigorously defined using Pydantic models. This provides strong data validation, clear error messages, and automatic generation of OpenAPI documentation.

-   `TranslationRequest` / `TranslationResponse`: Define the structure for translation jobs.
-   `APIKeyRequest` / `APIKeyResponse`: Manage the setting and status of provider API keys.
-   `AuthRequest` / `AuthResponse`: Handle the authentication flow.
-   `HealthResponse`: Provides a structured overview of the server's status.

---

## 5. API Endpoints

The server exposes a comprehensive set of RESTful endpoints:

-   `GET /api/health`: A public endpoint to check the health and availability of the server and its components.
-   `POST /api/auth`: Authenticates the user with the master password and returns a session token.
-   `POST /api/translate`: The core endpoint for performing translations. Requires an authenticated session.
-   `GET /api/providers`: Lists all available AI providers and indicates whether their API keys are configured.
-   `POST /api/providers/{provider_id}/key`: Securely sets or updates the API key for a specific provider.
-   `DELETE /api/providers/{provider_id}/key`: Removes the API key for a provider.

---

## 6. Resilience and Configuration

The server is designed to start up and run even if some components are missing.

-   **Optional Dependencies**: It uses `try/except` blocks to gracefully handle `ImportError` for optional dependencies like `FastAPI` or the secure backend modules.
-   **Clear Startup Messaging**: The `main()` function provides clear, informative logging upon startup, indicating the status of critical components like cryptography and secure storage.
