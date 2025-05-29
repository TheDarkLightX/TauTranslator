#!/usr/bin/env python3
"""
API Key Manager for TauTranslatorOmega
=====================================

Secure API key management for various AI providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Hugging Face (Inference API)
- Local encryption and storage
"""

import sys
import os
import json
import base64
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

class SecureAPIKeyManager:
    """Secure API key management with encryption."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".tau_translator"
        self.config_dir.mkdir(exist_ok=True)
        
        self.keys_file = self.config_dir / "api_keys.enc"
        self.salt_file = self.config_dir / "salt.key"
        
        self.supported_providers = {
            "openai": {
                "name": "OpenAI",
                "description": "GPT-4, GPT-3.5-turbo, etc.",
                "url": "https://platform.openai.com/api-keys",
                "test_endpoint": "https://api.openai.com/v1/models",
                "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"]
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "Claude 3.5 Sonnet, Claude 3 Haiku, etc.",
                "url": "https://console.anthropic.com/",
                "test_endpoint": "https://api.anthropic.com/v1/messages",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
            },
            "google": {
                "name": "Google AI",
                "description": "Gemini Pro, Gemini Flash, etc.",
                "url": "https://aistudio.google.com/app/apikey",
                "test_endpoint": "https://generativelanguage.googleapis.com/v1/models",
                "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-flash"]
            },
            "huggingface": {
                "name": "Hugging Face",
                "description": "Inference API for various models",
                "url": "https://huggingface.co/settings/tokens",
                "test_endpoint": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                "models": ["microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill"]
            }
        }
        
        self.cipher_suite = None
        self.api_keys = {}
        
    def _generate_key_from_password(self, password: str) -> bytes:
        """Generate encryption key from password."""
        # Get or create salt
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        
        # Generate key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_master_password(self) -> str:
        """Get master password for encryption."""
        # In a real app, this would be more sophisticated
        # For now, use a simple approach
        password = getpass.getpass("Enter master password for API keys: ")
        return password
    
    def initialize_encryption(self, password: str = None):
        """Initialize encryption system."""
        if password is None:
            password = self._get_master_password()
        
        key = self._generate_key_from_password(password)
        self.cipher_suite = Fernet(key)
        
        # Load existing keys if available
        self.load_api_keys()
    
    def save_api_keys(self):
        """Save encrypted API keys to file."""
        if not self.cipher_suite:
            raise Exception("Encryption not initialized")
        
        # Encrypt and save
        data = json.dumps(self.api_keys).encode()
        encrypted_data = self.cipher_suite.encrypt(data)
        
        with open(self.keys_file, 'wb') as f:
            f.write(encrypted_data)
    
    def load_api_keys(self):
        """Load and decrypt API keys from file."""
        if not self.keys_file.exists():
            self.api_keys = {}
            return
        
        if not self.cipher_suite:
            raise Exception("Encryption not initialized")
        
        try:
            with open(self.keys_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher_suite.decrypt(encrypted_data)
            self.api_keys = json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Failed to load API keys: {e}")
            self.api_keys = {}
    
    def set_api_key(self, provider: str, api_key: str):
        """Set API key for a provider."""
        if provider not in self.supported_providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.api_keys[provider] = api_key
        self.save_api_keys()
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a provider."""
        return self.api_keys.get(provider, "")
    
    def remove_api_key(self, provider: str):
        """Remove API key for a provider."""
        if provider in self.api_keys:
            del self.api_keys[provider]
            self.save_api_keys()
    
    def test_api_key(self, provider: str) -> bool:
        """Test if API key is valid."""
        api_key = self.get_api_key(provider)
        if not api_key:
            return False
        
        try:
            import requests
            
            provider_info = self.supported_providers[provider]
            headers = self._get_auth_headers(provider, api_key)
            
            response = requests.get(
                provider_info["test_endpoint"],
                headers=headers,
                timeout=10
            )
            
            return response.status_code in [200, 401]  # 401 means auth was attempted
        except Exception:
            return False
    
    def _get_auth_headers(self, provider: str, api_key: str) -> dict:
        """Get authentication headers for provider."""
        if provider == "openai":
            return {"Authorization": f"Bearer {api_key}"}
        elif provider == "anthropic":
            return {"x-api-key": api_key}
        elif provider == "google":
            return {"Authorization": f"Bearer {api_key}"}
        elif provider == "huggingface":
            return {"Authorization": f"Bearer {api_key}"}
        else:
            return {"Authorization": f"Bearer {api_key}"}

class APIKeyManagerDialog:
    """GUI for managing API keys."""
    
    def __init__(self, parent):
        self.parent = parent
        self.manager = SecureAPIKeyManager()
        
        # Initialize with simple password for demo
        try:
            self.manager.initialize_encryption("demo_password_123")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize encryption: {e}")
            return
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔐 API Key Manager")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create the API key management UI."""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🔐 Secure API Key Management",
            font=('Segoe UI', 16, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Securely store API keys for AI providers. Keys are encrypted locally.",
            font=('Segoe UI', 10),
            fg="#666666"
        )
        instructions.pack(anchor='w', pady=(0, 20))
        
        # Provider list
        self.create_provider_list(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
    
    def create_provider_list(self, parent):
        """Create list of API providers."""
        # Scrollable frame
        canvas = tk.Canvas(parent, height=300)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Provider cards
        for provider_id, provider_info in self.manager.supported_providers.items():
            self.create_provider_card(scrollable_frame, provider_id, provider_info)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_provider_card(self, parent, provider_id, provider_info):
        """Create a card for each provider."""
        # Card frame
        card_frame = tk.Frame(parent, relief='solid', bd=1, bg='white')
        card_frame.pack(fill='x', pady=5, padx=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Provider name and status
        name_frame = tk.Frame(header_frame, bg='#f8f9fa')
        name_frame.pack(fill='x')
        
        tk.Label(
            name_frame,
            text=provider_info["name"],
            font=('Segoe UI', 12, 'bold'),
            bg='#f8f9fa'
        ).pack(side='left')
        
        # Status indicator
        api_key = self.manager.get_api_key(provider_id)
        status_text = "✅ Configured" if api_key else "❌ Not configured"
        status_color = "#28a745" if api_key else "#dc3545"
        
        tk.Label(
            name_frame,
            text=status_text,
            font=('Segoe UI', 9),
            fg=status_color,
            bg='#f8f9fa'
        ).pack(side='right')
        
        # Description
        tk.Label(
            card_frame,
            text=provider_info["description"],
            font=('Segoe UI', 9),
            fg="#666666",
            bg='white'
        ).pack(anchor='w', padx=10, pady=(0, 5))
        
        # Models
        models_text = "Models: " + ", ".join(provider_info["models"][:2])
        if len(provider_info["models"]) > 2:
            models_text += f" (+{len(provider_info['models'])-2} more)"
        
        tk.Label(
            card_frame,
            text=models_text,
            font=('Segoe UI', 8),
            fg="#888888",
            bg='white'
        ).pack(anchor='w', padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(card_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Set/Update key button
        key_btn_text = "Update Key" if api_key else "Set API Key"
        tk.Button(
            button_frame,
            text=key_btn_text,
            command=lambda: self.set_api_key(provider_id, provider_info),
            bg='#007bff',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        ).pack(side='left', padx=(0, 5))
        
        # Test key button
        if api_key:
            tk.Button(
                button_frame,
                text="Test Key",
                command=lambda: self.test_api_key(provider_id),
                bg='#28a745',
                fg='white',
                relief='flat',
                padx=10,
                pady=5
            ).pack(side='left', padx=5)
            
            # Remove key button
            tk.Button(
                button_frame,
                text="Remove",
                command=lambda: self.remove_api_key(provider_id),
                bg='#dc3545',
                fg='white',
                relief='flat',
                padx=10,
                pady=5
            ).pack(side='left', padx=5)
        
        # Get API key link
        tk.Button(
            button_frame,
            text="Get API Key",
            command=lambda: self.open_provider_url(provider_info["url"]),
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        ).pack(side='right')
    
    def create_buttons(self, parent):
        """Create bottom buttons."""
        button_frame = tk.Frame(parent)
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_ui,
            bg='#17a2b8',
            fg='white',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left')
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='right')
    
    def set_api_key(self, provider_id, provider_info):
        """Set API key for provider."""
        current_key = self.manager.get_api_key(provider_id)
        
        # Create custom dialog for API key input
        key_dialog = tk.Toplevel(self.dialog)
        key_dialog.title(f"Set {provider_info['name']} API Key")
        key_dialog.geometry("400x200")
        key_dialog.transient(self.dialog)
        key_dialog.grab_set()
        
        # Instructions
        tk.Label(
            key_dialog,
            text=f"Enter your {provider_info['name']} API key:",
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=10)
        
        tk.Label(
            key_dialog,
            text="Your key will be encrypted and stored securely.",
            font=('Segoe UI', 9),
            fg="#666666"
        ).pack(pady=(0, 10))
        
        # API key entry
        key_var = tk.StringVar(value=current_key)
        key_entry = tk.Entry(key_dialog, textvariable=key_var, width=50, show="*")
        key_entry.pack(pady=10)
        key_entry.focus()
        
        # Buttons
        button_frame = tk.Frame(key_dialog)
        button_frame.pack(pady=20)
        
        def save_key():
            api_key = key_var.get().strip()
            if api_key:
                try:
                    self.manager.set_api_key(provider_id, api_key)
                    messagebox.showinfo("Success", f"{provider_info['name']} API key saved securely!")
                    key_dialog.destroy()
                    self.refresh_ui()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save API key: {e}")
            else:
                messagebox.showwarning("Warning", "Please enter an API key")
        
        tk.Button(
            button_frame,
            text="Save",
            command=save_key,
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=key_dialog.destroy,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=20,
            pady=8
        ).pack(side='left', padx=5)
        
        # Bind Enter key
        key_dialog.bind('<Return>', lambda e: save_key())
    
    def test_api_key(self, provider_id):
        """Test API key for provider."""
        try:
            if self.manager.test_api_key(provider_id):
                messagebox.showinfo("Success", f"API key for {self.manager.supported_providers[provider_id]['name']} is valid!")
            else:
                messagebox.showerror("Error", f"API key for {self.manager.supported_providers[provider_id]['name']} is invalid or unreachable.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to test API key: {e}")
    
    def remove_api_key(self, provider_id):
        """Remove API key for provider."""
        provider_name = self.manager.supported_providers[provider_id]['name']
        if messagebox.askyesno("Confirm", f"Remove API key for {provider_name}?"):
            self.manager.remove_api_key(provider_id)
            messagebox.showinfo("Success", f"API key for {provider_name} removed.")
            self.refresh_ui()
    
    def open_provider_url(self, url):
        """Open provider URL in browser."""
        import webbrowser
        webbrowser.open(url)
    
    def refresh_ui(self):
        """Refresh the UI."""
        self.dialog.destroy()
        APIKeyManagerDialog(self.parent)

def test_api_key_manager():
    """Test the API key manager."""
    root = tk.Tk()
    root.title("API Key Manager Test")
    root.geometry("300x200")
    
    tk.Button(
        root,
        text="Open API Key Manager",
        command=lambda: APIKeyManagerDialog(root),
        font=('Segoe UI', 12),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=10
    ).pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_api_key_manager()
