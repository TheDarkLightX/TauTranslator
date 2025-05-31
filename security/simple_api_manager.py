#!/usr/bin/env python3
"""
Simple API Manager for TauTranslatorOmega
========================================

A simplified API key manager that works without complex dependencies.
Stores API keys in a simple encrypted format using basic Python libraries.
"""

import sys
import os
import json
import base64
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path

class SimpleAPIManager:
    """Simple API key manager with basic security."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".tau_translator"
        self.config_dir.mkdir(exist_ok=True)
        
        self.keys_file = self.config_dir / "api_keys.json"
        
        self.supported_providers = {
            "openai": {
                "name": "OpenAI",
                "description": "GPT-4, GPT-3.5-turbo, etc.",
                "url": "https://platform.openai.com/api-keys",
                "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
                "example": "sk-..."
            },
            "anthropic": {
                "name": "Anthropic",
                "description": "Claude 3.5 Sonnet, Claude 3 Haiku, etc.",
                "url": "https://console.anthropic.com/",
                "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"],
                "example": "sk-ant-..."
            },
            "google": {
                "name": "Google AI",
                "description": "Gemini Pro, Gemini Flash, etc.",
                "url": "https://aistudio.google.com/app/apikey",
                "models": ["gemini-pro", "gemini-1.5-flash"],
                "example": "AIza..."
            },
            "huggingface": {
                "name": "Hugging Face",
                "description": "Inference API for various models",
                "url": "https://huggingface.co/settings/tokens",
                "models": ["microsoft/DialoGPT-medium", "facebook/blenderbot-400M-distill"],
                "example": "hf_..."
            }
        }
        
        self.api_keys = {}
        self.load_api_keys()
    
    def _simple_encode(self, text):
        """Simple encoding (not secure, but better than plain text)."""
        return base64.b64encode(text.encode()).decode()
    
    def _simple_decode(self, encoded_text):
        """Simple decoding."""
        try:
            return base64.b64decode(encoded_text.encode()).decode()
        except:
            return encoded_text  # Fallback for plain text
    
    def save_api_keys(self):
        """Save API keys to file."""
        # Simple encoding for basic obfuscation
        encoded_keys = {}
        for provider, key in self.api_keys.items():
            if key:
                encoded_keys[provider] = self._simple_encode(key)
        
        try:
            with open(self.keys_file, 'w') as f:
                json.dump(encoded_keys, f, indent=2)
        except Exception as e:
            print(f"Failed to save API keys: {e}")
    
    def load_api_keys(self):
        """Load API keys from file."""
        if not self.keys_file.exists():
            self.api_keys = {}
            return
        
        try:
            with open(self.keys_file, 'r') as f:
                encoded_keys = json.load(f)
            
            self.api_keys = {}
            for provider, encoded_key in encoded_keys.items():
                self.api_keys[provider] = self._simple_decode(encoded_key)
                
        except Exception as e:
            print(f"Failed to load API keys: {e}")
            self.api_keys = {}
    
    def set_api_key(self, provider, api_key):
        """Set API key for a provider."""
        if provider not in self.supported_providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.api_keys[provider] = api_key
        self.save_api_keys()
    
    def get_api_key(self, provider):
        """Get API key for a provider."""
        return self.api_keys.get(provider, "")
    
    def remove_api_key(self, provider):
        """Remove API key for a provider."""
        if provider in self.api_keys:
            del self.api_keys[provider]
            self.save_api_keys()
    
    def has_api_key(self, provider):
        """Check if provider has API key."""
        return bool(self.get_api_key(provider))

class SimpleAPIManagerDialog:
    """Simple dialog for managing API keys."""
    
    def __init__(self, parent):
        self.parent = parent
        self.manager = SimpleAPIManager()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔐 API Key Manager")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create the UI."""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🔐 API Key Manager",
            font=('Segoe UI', 16, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack(expand=True)
        
        # Instructions
        instructions_frame = tk.Frame(self.dialog, bg="#f8f9fa")
        instructions_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            instructions_frame,
            text="Manage API keys for AI providers. Keys are stored locally with basic encoding.",
            font=('Segoe UI', 10),
            bg="#f8f9fa",
            fg="#666666"
        ).pack()
        
        # Main content
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Provider cards
        for provider_id, provider_info in self.manager.supported_providers.items():
            self.create_provider_card(main_frame, provider_id, provider_info)
        
        # Bottom buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_ui,
            bg='#17a2b8',
            fg='white',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='left')
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='right')
    
    def create_provider_card(self, parent, provider_id, provider_info):
        """Create a card for each provider."""
        # Card frame
        card_frame = tk.Frame(parent, relief='solid', bd=1, bg='white')
        card_frame.pack(fill='x', pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg='#f8f9fa')
        header_frame.pack(fill='x', padx=10, pady=10)
        
        # Provider name and status
        tk.Label(
            header_frame,
            text=provider_info["name"],
            font=('Segoe UI', 12, 'bold'),
            bg='#f8f9fa'
        ).pack(side='left')
        
        # Status
        has_key = self.manager.has_api_key(provider_id)
        status_text = "✅ Configured" if has_key else "❌ Not configured"
        status_color = "#28a745" if has_key else "#dc3545"
        
        tk.Label(
            header_frame,
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
        
        # Example format
        tk.Label(
            card_frame,
            text=f"Format: {provider_info['example']}",
            font=('Segoe UI', 8),
            fg="#888888",
            bg='white'
        ).pack(anchor='w', padx=10, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(card_frame, bg='white')
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Set/Update key button
        key_btn_text = "Update Key" if has_key else "Set API Key"
        tk.Button(
            button_frame,
            text=key_btn_text,
            command=lambda: self.set_api_key(provider_id, provider_info),
            bg='#007bff',
            fg='white',
            relief='flat',
            padx=10,
            pady=5,
            font=('Segoe UI', 9)
        ).pack(side='left', padx=(0, 5))
        
        # Remove key button
        if has_key:
            tk.Button(
                button_frame,
                text="Remove",
                command=lambda: self.remove_api_key(provider_id, provider_info),
                bg='#dc3545',
                fg='white',
                relief='flat',
                padx=10,
                pady=5,
                font=('Segoe UI', 9)
            ).pack(side='left', padx=5)
        
        # Get API key link
        tk.Button(
            button_frame,
            text="Get API Key",
            command=lambda: self.open_provider_url(provider_info["url"]),
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=10,
            pady=5,
            font=('Segoe UI', 9)
        ).pack(side='right')
    
    def set_api_key(self, provider_id, provider_info):
        """Set API key for provider."""
        current_key = self.manager.get_api_key(provider_id)
        
        # Simple input dialog
        api_key = simpledialog.askstring(
            f"Set {provider_info['name']} API Key",
            f"Enter your {provider_info['name']} API key:\n\nFormat: {provider_info['example']}\n\nKey will be stored locally with basic encoding.",
            initialvalue=current_key,
            show='*'
        )
        
        if api_key and api_key.strip():
            try:
                self.manager.set_api_key(provider_id, api_key.strip())
                messagebox.showinfo("Success", f"{provider_info['name']} API key saved!")
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def remove_api_key(self, provider_id, provider_info):
        """Remove API key for provider."""
        if messagebox.askyesno("Confirm", f"Remove API key for {provider_info['name']}?"):
            self.manager.remove_api_key(provider_id)
            messagebox.showinfo("Success", f"API key for {provider_info['name']} removed.")
            self.refresh_ui()
    
    def open_provider_url(self, url):
        """Open provider URL in browser."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            messagebox.showinfo("URL", f"Please visit: {url}")
    
    def refresh_ui(self):
        """Refresh the UI."""
        self.dialog.destroy()
        SimpleAPIManagerDialog(self.parent)

def test_simple_api_manager():
    """Test the simple API manager."""
    root = tk.Tk()
    root.title("Simple API Manager Test")
    root.geometry("300x200")
    
    tk.Label(
        root,
        text="Simple API Key Manager",
        font=('Segoe UI', 14, 'bold')
    ).pack(pady=20)
    
    tk.Button(
        root,
        text="Open API Manager",
        command=lambda: SimpleAPIManagerDialog(root),
        font=('Segoe UI', 12),
        bg='#007bff',
        fg='white',
        padx=20,
        pady=10
    ).pack(pady=10)
    
    tk.Label(
        root,
        text="No external dependencies required!",
        font=('Segoe UI', 9),
        fg="#666666"
    ).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_simple_api_manager()
