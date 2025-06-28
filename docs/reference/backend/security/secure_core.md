Module backend.security.secure_core
===================================
Provides secure, encrypted storage for sensitive data like API keys.
Uses Fernet symmetric encryption from the cryptography library.

Classes
-------

`SecureStorage(master_password_hash: str, storage_path: str = 'secure_storage.enc')`
:   Manages the encryption and decryption of API keys.

    ### Methods

    `get_all_api_keys(self) ‑> dict`
    :   Returns all stored provider IDs and their keys.

    `get_api_key(self, provider_id: str) ‑> str | None`
    :   Retrieves an API key for a given provider.

    `has_api_key(self, provider_id: str) ‑> bool`
    :   Checks if an API key for a given provider exists.

    `remove_api_key(self, provider_id: str)`
    :   Removes an API key for a given provider.

    `save_api_key(self, provider_id: str, api_key: str)`
    :   Saves or updates an API key for a given provider.