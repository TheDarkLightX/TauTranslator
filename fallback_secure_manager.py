#!/usr/bin/env python3
"""
Fallback Secure Manager
=======================

Secure API key manager that works without external dependencies.
Uses Python's built-in libraries for reasonable security.
"""

import os
import json
import hashlib
import secrets
import base64
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
import time

class FallbackSecureStorage:
    """Secure storage using only Python built-in libraries."""
    
    def __init__(self):
        # Create secure directory
        self.config_dir = Path.home() / ".tau_translator_fallback"
        self.config_dir.mkdir(mode=0o700, exist_ok=True)
        
        # File paths
        self.keys_file = self.config_dir / "keys.enc"
        self.salt_file = self.config_dir / "salt.bin"
        self.auth_file = self.config_dir / "auth.hash"
        
        # Set permissions
        os.chmod(self.config_dir, 0o700)
        
        # State
        self.authenticated = False
        self.api_keys = {}
        self.encryption_key = None
    
    def _secure_random_bytes(self, length: int) -> bytes:
        """Generate secure random bytes."""
        return secrets.token_bytes(length)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive key using PBKDF2 (built-in)."""
        # Use hashlib.pbkdf2_hmac (available in Python 3.4+)
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    
    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Simple XOR encryption with key stretching."""
        # Not as secure as AES, but better than plaintext
        # Stretch key to data length
        key_stream = b''
        for i in range(0, len(data), len(key)):
            key_stream += key
        key_stream = key_stream[:len(data)]
        
        # XOR encrypt
        encrypted = bytes(a ^ b for a, b in zip(data, key_stream))
        
        # Add random prefix for additional security
        prefix = self._secure_random_bytes(16)
        return prefix + encrypted
    
    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Decrypt XOR encrypted data."""
        # Remove prefix
        data = encrypted_data[16:]
        
        # Stretch key
        key_stream = b''
        for i in range(0, len(data), len(key)):
            key_stream += key
        key_stream = key_stream[:len(data)]
        
        # XOR decrypt
        return bytes(a ^ b for a, b in zip(data, key_stream))
    
    def _secure_write_file(self, filepath: Path, data: bytes):
        """Atomic write with secure permissions."""
        temp_file = filepath.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'wb') as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            
            os.chmod(temp_file, 0o600)
            temp_file.replace(filepath)
            
        except Exception:
            if temp_file.exists():
                temp_file.unlink()
            raise
    
    def setup_encryption(self, password: str) -> bool:
        """Set up encryption for first time."""
        try:
            # Generate salt
            salt = self._secure_random_bytes(32)
            
            # Derive key and hash password
            self.encryption_key = self._derive_key(password, salt)
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            # Save salt and hash
            self._secure_write_file(self.salt_file, salt)
            self._secure_write_file(self.auth_file, password_hash)
            
            # Initialize empty storage
            self.api_keys = {}
            self._save_encrypted_data()
            
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"Setup failed: {e}")
            return False
    
    def unlock_with_password(self, password: str) -> bool:
        """Unlock with password."""
        try:
            # Load salt and hash
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
            
            with open(self.auth_file, 'rb') as f:
                stored_hash = f.read()
            
            # Verify password
            computed_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            
            if secrets.compare_digest(stored_hash, computed_hash):
                self.encryption_key = self._derive_key(password, salt)
                self._load_encrypted_data()
                self.authenticated = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Unlock failed: {e}")
            return False
    
    def _save_encrypted_data(self):
        """Save encrypted data."""
        if not self.encryption_key or not self.authenticated:
            raise Exception("Not authenticated")
        
        data = {
            'api_keys': self.api_keys,
            'timestamp': time.time()
        }
        
        # Encrypt
        plaintext = json.dumps(data).encode('utf-8')
        encrypted = self._encrypt_data(plaintext, self.encryption_key)
        
        # Save
        self._secure_write_file(self.keys_file, encrypted)
    
    def _load_encrypted_data(self):
        """Load encrypted data."""
        if not self.encryption_key:
            raise Exception("Not authenticated")
        
        if not self.keys_file.exists():
            self.api_keys = {}
            return
        
        with open(self.keys_file, 'rb') as f:
            encrypted_data = f.read()
        
        # Decrypt
        plaintext = self._decrypt_data(encrypted_data, self.encryption_key)
        data = json.loads(plaintext.decode('utf-8'))
        
        self.api_keys = data.get('api_keys', {})
    
    def store_api_key(self, provider: str, api_key: str):
        """Store API key."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        self.api_keys[provider] = api_key
        self._save_encrypted_data()
    
    def get_api_key(self, provider: str) -> str:
        """Get API key."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        return self.api_keys.get(provider, "")
    
    def remove_api_key(self, provider: str):
        """Remove API key."""
        if not self.authenticated:
            raise Exception("Not authenticated")
        
        if provider in self.api_keys:
            del self.api_keys[provider]
            self._save_encrypted_data()
    
    def has_api_key(self, provider: str) -> bool:
        """Check if API key exists."""
        if not self.authenticated:
            return False
        return provider in self.api_keys
    
    def is_first_time(self) -> bool:
        """Check if first time."""
        return not self.auth_file.exists()
    
    def secure_shutdown(self):
        """Clear sensitive data."""
        if hasattr(self, 'api_keys'):
            self.api_keys.clear()
        self.encryption_key = None
        self.authenticated = False
    
    def get_storage_info(self) -> dict:
        """Get storage information."""
        return {
            'directory': str(self.config_dir),
            'encrypted_keys': str(self.keys_file),
            'salt_file': str(self.salt_file),
            'auth_file': str(self.auth_file),
            'permissions': '0o700 (owner only)',
            'encryption': 'PBKDF2 + XOR (fallback)',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }

class FallbackSecureManager:
    """Fallback secure manager with built-in libraries only."""
    
    def __init__(self, parent):
        self.parent = parent
        self.storage = FallbackSecureStorage()
        
        # Show fallback notice
        messagebox.showinfo(
            "Fallback Security Mode",
            "Using fallback security (Python built-in libraries).\n\n"
            "For maximum security, install cryptography:\n"
            "sudo apt install python3-cryptography\n\n"
            "Current security: PBKDF2 + XOR encryption"
        )
        
        # Authenticate
        if not self.authenticate():
            return
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔐 Fallback Secure API Manager")

        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Calculate responsive size (minimum 700x600, max 85% of screen)
        width = max(700, min(1000, int(screen_width * 0.7)))
        height = max(600, min(800, int(screen_height * 0.8)))

        self.dialog.geometry(f"{width}x{height}")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)

        # Center dialog
        self.dialog.update_idletasks()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")

        # Set minimum size
        self.dialog.minsize(700, 600)
        
        self.dialog.protocol("WM_DELETE_WINDOW", self.secure_close)
        self.create_ui()
    
    def authenticate(self) -> bool:
        """Authenticate user."""
        try:
            if self.storage.is_first_time():
                # First time setup
                password = tk.simpledialog.askstring(
                    "Create Master Password",
                    "Create a strong master password:",
                    show='*'
                )
                
                if not password:
                    return False
                
                if len(password) < 8:
                    messagebox.showerror("Error", "Password must be at least 8 characters")
                    return False
                
                # Confirm password
                confirm = tk.simpledialog.askstring(
                    "Confirm Password",
                    "Confirm your master password:",
                    show='*'
                )
                
                if password != confirm:
                    messagebox.showerror("Error", "Passwords do not match")
                    return False
                
                if self.storage.setup_encryption(password):
                    messagebox.showinfo("Success", "Fallback secure storage initialized!")
                    return True
                else:
                    messagebox.showerror("Error", "Failed to initialize storage")
                    return False
            
            else:
                # Existing storage
                password = tk.simpledialog.askstring(
                    "Enter Master Password",
                    "Enter your master password:",
                    show='*'
                )
                
                if not password:
                    return False
                
                if self.storage.unlock_with_password(password):
                    return True
                else:
                    messagebox.showerror("Error", "Incorrect password")
                    return False
        
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")
            return False
    
    def create_ui(self):
        """Create UI."""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.pack(expand=True)
        
        tk.Label(
            title_frame,
            text="🔐 Fallback Secure API Manager",
            font=('Segoe UI', 16, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack()
        
        tk.Label(
            title_frame,
            text="⚠️ Fallback Mode • PBKDF2 + XOR Encryption",
            font=('Segoe UI', 10),
            bg="#2c3e50",
            fg="#f39c12"
        ).pack()
        
        # Main content
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Notice
        notice_frame = tk.Frame(main_frame, bg="#fff3cd", relief='solid', bd=1)
        notice_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            notice_frame,
            text="⚠️ Fallback Security Mode Active",
            font=('Segoe UI', 12, 'bold'),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=(10, 5))
        
        tk.Label(
            notice_frame,
            text="For maximum security, install cryptography: sudo apt install python3-cryptography",
            font=('Segoe UI', 10),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=(0, 10))
        
        # Simple provider list
        providers = {
            "openrouter": "OpenRouter (Recommended)",
            "openai": "OpenAI Direct",
            "anthropic": "Anthropic Direct"
        }
        
        for provider_id, provider_name in providers.items():
            self.create_simple_provider_card(main_frame, provider_id, provider_name)
        
        # Storage info
        self.create_storage_info(main_frame)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(
            button_frame,
            text="🔒 Close",
            command=self.secure_close,
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=15,
            pady=8
        ).pack(side='right')
    
    def create_simple_provider_card(self, parent, provider_id, provider_name):
        """Create simple provider card."""
        card_frame = tk.Frame(parent, relief='solid', bd=1, bg='white')
        card_frame.pack(fill='x', pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg='white')
        header_frame.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            header_frame,
            text=provider_name,
            font=('Segoe UI', 12, 'bold'),
            bg='white'
        ).pack(side='left')
        
        # Status
        has_key = self.storage.has_api_key(provider_id)
        status_text = "🔒 Stored" if has_key else "❌ Not set"
        status_color = "#28a745" if has_key else "#dc3545"
        
        tk.Label(
            header_frame,
            text=status_text,
            font=('Segoe UI', 10, 'bold'),
            fg=status_color,
            bg='white'
        ).pack(side='right')
        
        # Buttons
        button_frame = tk.Frame(card_frame, bg='white')
        button_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # Set key button
        btn_text = "Update Key" if has_key else "Set API Key"
        tk.Button(
            button_frame,
            text=btn_text,
            command=lambda: self.set_api_key(provider_id, provider_name),
            bg='#007bff',
            fg='white',
            relief='flat',
            padx=10,
            pady=5
        ).pack(side='left', padx=(0, 5))
        
        # Remove button
        if has_key:
            tk.Button(
                button_frame,
                text="Remove",
                command=lambda: self.remove_api_key(provider_id, provider_name),
                bg='#dc3545',
                fg='white',
                relief='flat',
                padx=10,
                pady=5
            ).pack(side='left')
    
    def create_storage_info(self, parent):
        """Create storage info section."""
        info_frame = tk.Frame(parent, bg="#d1ecf1", relief='solid', bd=1)
        info_frame.pack(fill='x', pady=(15, 0))
        
        tk.Label(
            info_frame,
            text="📁 Storage Information",
            font=('Segoe UI', 12, 'bold'),
            bg="#d1ecf1",
            fg="#0c5460"
        ).pack(pady=(10, 5))
        
        storage_info = self.storage.get_storage_info()
        
        info_text = f"Location: {storage_info['directory']}\n"
        info_text += f"Encryption: {storage_info['encryption']}\n"
        info_text += f"Key Derivation: {storage_info['key_derivation']}"
        
        tk.Label(
            info_frame,
            text=info_text,
            font=('Consolas', 9),
            bg="#d1ecf1",
            fg="#0c5460",
            justify='left'
        ).pack(anchor='w', padx=15, pady=(0, 10))
    
    def set_api_key(self, provider_id, provider_name):
        """Set API key."""
        current_key = self.storage.get_api_key(provider_id)
        
        api_key = tk.simpledialog.askstring(
            f"Set {provider_name} API Key",
            f"Enter your {provider_name} API key:",
            initialvalue=current_key,
            show='*'
        )
        
        if api_key and api_key.strip():
            try:
                self.storage.store_api_key(provider_id, api_key.strip())
                messagebox.showinfo("Success", f"{provider_name} API key saved!")
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def remove_api_key(self, provider_id, provider_name):
        """Remove API key."""
        if messagebox.askyesno("Confirm", f"Remove API key for {provider_name}?"):
            try:
                self.storage.remove_api_key(provider_id)
                messagebox.showinfo("Success", f"API key for {provider_name} removed.")
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove API key: {e}")
    
    def refresh_ui(self):
        """Refresh UI."""
        self.dialog.destroy()
        FallbackSecureManager(self.parent)
    
    def secure_close(self):
        """Secure close."""
        self.storage.secure_shutdown()
        self.dialog.destroy()

def test_fallback_manager():
    """Test fallback manager."""
    root = tk.Tk()
    root.title("Fallback Secure Manager Test")
    root.geometry("300x200")
    
    tk.Button(
        root,
        text="Open Fallback Manager",
        command=lambda: FallbackSecureManager(root),
        font=('Segoe UI', 12),
        bg='#f39c12',
        fg='white',
        padx=20,
        pady=10
    ).pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_fallback_manager()
