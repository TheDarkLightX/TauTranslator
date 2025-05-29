#!/usr/bin/env python3
"""
Real Secure API Manager
=======================

This is the ACTUAL secure implementation that:
1. Uses real AES-256-GCM encryption
2. Shows exactly where keys are stored
3. Has proper key entry dialogs
4. Implements real security, not just a secure-looking GUI
"""

import tkinter as tk
from tkinter import messagebox, ttk
from secure_core import SecureStorage, CRYPTO_AVAILABLE
from provider_config import provider_config
from secure_password_dialog import SecurePasswordDialog
from api_key_entry_dialog import APIKeyEntryDialog

class RealSecureAPIManager:
    """Real secure API manager with actual security."""
    
    def __init__(self, parent):
        self.parent = parent
        self.storage = SecureStorage()
        
        # Check dependencies
        if not CRYPTO_AVAILABLE:
            messagebox.showerror(
                "Missing Dependency",
                "Secure API management requires the cryptography library.\n\n"
                "Install with: pip install cryptography\n\n"
                "This provides real AES-256-GCM encryption for your API keys."
            )
            return
        
        # Authenticate user
        if not self.authenticate():
            return
        
        # Create main dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔐 Real Secure API Manager")

        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Calculate responsive size (minimum 800x700, max 90% of screen)
        width = max(800, min(1200, int(screen_width * 0.8)))
        height = max(700, min(900, int(screen_height * 0.85)))

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
        self.dialog.minsize(800, 700)
        
        # Security: Clear data on close
        self.dialog.protocol("WM_DELETE_WINDOW", self.secure_close)
        
        self.create_ui()
    
    def authenticate(self) -> bool:
        """Authenticate user with master password."""
        try:
            if self.storage.is_first_time():
                # First time setup
                password_dialog = SecurePasswordDialog(
                    self.parent, 
                    "Create Master Password", 
                    is_new=True
                )
                self.parent.wait_window(password_dialog.dialog)
                
                if not password_dialog.password:
                    return False
                
                # Confirm password
                confirm_dialog = SecurePasswordDialog(
                    self.parent,
                    "Confirm Master Password",
                    is_new=False
                )
                self.parent.wait_window(confirm_dialog.dialog)
                
                if (not confirm_dialog.password or 
                    confirm_dialog.password != password_dialog.password):
                    messagebox.showerror("Error", "Passwords do not match")
                    return False
                
                # Setup encryption
                if self.storage.setup_encryption(password_dialog.password):
                    messagebox.showinfo(
                        "Success", 
                        "Secure storage initialized!\n\n"
                        "Your API keys will be encrypted with AES-256-GCM."
                    )
                    return True
                else:
                    messagebox.showerror("Error", "Failed to initialize secure storage")
                    return False
            
            else:
                # Existing storage - unlock
                password_dialog = SecurePasswordDialog(
                    self.parent,
                    "Enter Master Password",
                    is_new=False
                )
                self.parent.wait_window(password_dialog.dialog)
                
                if not password_dialog.password:
                    return False
                
                if self.storage.unlock_with_password(password_dialog.password):
                    return True
                else:
                    messagebox.showerror("Authentication Failed", "Incorrect password")
                    return False
        
        except Exception as e:
            messagebox.showerror("Error", f"Authentication failed: {e}")
            return False
    
    def create_ui(self):
        """Create the main UI."""
        # Header
        self.create_header()
        
        # Main content with tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # API Keys tab
        keys_frame = ttk.Frame(notebook)
        notebook.add(keys_frame, text="🔑 API Keys")
        self.create_keys_tab(keys_frame)
        
        # Security Info tab
        security_frame = ttk.Frame(notebook)
        notebook.add(security_frame, text="🛡️ Security Info")
        self.create_security_tab(security_frame)
        
        # Bottom buttons
        self.create_bottom_buttons()
    
    def create_header(self):
        """Create header with security status."""
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.pack(expand=True)
        
        tk.Label(
            title_frame,
            text="🔐 Real Secure API Manager",
            font=('Segoe UI', 18, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack()
        
        tk.Label(
            title_frame,
            text="✅ AES-256-GCM Encrypted • ✅ Authenticated • ✅ OpenRouter Supported",
            font=('Segoe UI', 10),
            bg="#2c3e50",
            fg="#bdc3c7"
        ).pack()
    
    def create_keys_tab(self, parent):
        """Create API keys management tab."""
        # OpenRouter recommendation
        self.create_openrouter_recommendation(parent)
        
        # Provider list
        self.create_provider_list(parent)
    
    def create_openrouter_recommendation(self, parent):
        """Create OpenRouter recommendation section."""
        rec_frame = tk.Frame(parent, bg="#e8f5e8", relief='solid', bd=2)
        rec_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            rec_frame,
            text="💡 RECOMMENDED: Use OpenRouter for maximum value",
            font=('Segoe UI', 12, 'bold'),
            bg="#e8f5e8",
            fg="#2d5a2d"
        ).pack(pady=(10, 5))
        
        benefits = [
            "• Access 100+ AI models with one API key",
            "• Often 50-80% cheaper than direct provider APIs", 
            "• No need for multiple subscriptions",
            "• Latest models automatically available"
        ]
        
        for benefit in benefits:
            tk.Label(
                rec_frame,
                text=benefit,
                font=('Segoe UI', 10),
                bg="#e8f5e8",
                fg="#2d5a2d"
            ).pack(anchor='w', padx=20, pady=1)
        
        tk.Label(rec_frame, text="", bg="#e8f5e8").pack(pady=5)
    
    def create_provider_list(self, parent):
        """Create scrollable provider list."""
        # Scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Create provider cards
        for provider_id, provider_info in provider_config.get_sorted_providers():
            self.create_provider_card(scrollable_frame, provider_id, provider_info)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
    
    def create_provider_card(self, parent, provider_id, provider_info):
        """Create a provider card with real functionality."""
        # Card styling
        bg_color = "#f0f8ff" if provider_info.get('recommended') else "white"
        border_color = "#007bff" if provider_info.get('recommended') else "#dee2e6"
        
        card_frame = tk.Frame(parent, relief='solid', bd=2, bg=bg_color)
        card_frame.configure(highlightbackground=border_color)
        card_frame.pack(fill='x', pady=8, padx=5)
        
        # Recommended badge
        if provider_info.get('recommended'):
            badge_frame = tk.Frame(card_frame, bg="#007bff")
            badge_frame.pack(fill='x')
            
            tk.Label(
                badge_frame,
                text="⭐ RECOMMENDED",
                font=('Segoe UI', 8, 'bold'),
                bg="#007bff",
                fg="white"
            ).pack(pady=2)
        
        # Header with name and status
        header_frame = tk.Frame(card_frame, bg=bg_color)
        header_frame.pack(fill='x', padx=15, pady=(10, 5))
        
        tk.Label(
            header_frame,
            text=provider_info["name"],
            font=('Segoe UI', 13, 'bold'),
            bg=bg_color
        ).pack(side='left')
        
        # Real security status
        has_key = self.storage.has_api_key(provider_id)
        if has_key:
            status_text = "🔒 ENCRYPTED"
            status_color = "#28a745"
        else:
            status_text = "🔓 Not configured"
            status_color = "#dc3545"
        
        tk.Label(
            header_frame,
            text=status_text,
            font=('Segoe UI', 10, 'bold'),
            fg=status_color,
            bg=bg_color
        ).pack(side='right')
        
        # Description
        tk.Label(
            card_frame,
            text=provider_info["description"],
            font=('Segoe UI', 10),
            fg="#495057",
            bg=bg_color,
            wraplength=700,
            justify='left'
        ).pack(anchor='w', padx=15, pady=(0, 8))
        
        # Action buttons
        button_frame = tk.Frame(card_frame, bg=bg_color)
        button_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # Set/Update key button
        key_btn_text = "🔄 Update Key" if has_key else "🔑 Set API Key"
        key_btn_color = "#ffc107" if has_key else "#28a745"
        
        tk.Button(
            button_frame,
            text=key_btn_text,
            command=lambda: self.set_api_key(provider_id),
            bg=key_btn_color,
            fg='white' if key_btn_color != "#ffc107" else 'black',
            relief='flat',
            padx=12,
            pady=6,
            font=('Segoe UI', 9, 'bold')
        ).pack(side='left', padx=(0, 8))
        
        # Remove key button
        if has_key:
            tk.Button(
                button_frame,
                text="🗑️ Remove",
                command=lambda: self.remove_api_key(provider_id),
                bg='#dc3545',
                fg='white',
                relief='flat',
                padx=12,
                pady=6,
                font=('Segoe UI', 9)
            ).pack(side='left', padx=8)
        
        # Get API key button
        tk.Button(
            button_frame,
            text="🌐 Get API Key",
            command=lambda: self.open_provider_url(provider_info["url"]),
            bg='#17a2b8',
            fg='white',
            relief='flat',
            padx=12,
            pady=6,
            font=('Segoe UI', 9)
        ).pack(side='right')
    
    def create_security_tab(self, parent):
        """Create security information tab."""
        # Security status
        status_frame = tk.Frame(parent, bg="#f8f9fa", relief='solid', bd=1)
        status_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            status_frame,
            text="🛡️ Real Security Implementation",
            font=('Segoe UI', 14, 'bold'),
            bg="#f8f9fa"
        ).pack(pady=(15, 10))
        
        security_features = [
            "✅ AES-256-GCM authenticated encryption",
            "✅ Scrypt key derivation (memory-hard function)",
            "✅ Cryptographically secure random salt",
            "✅ Constant-time password verification",
            "✅ Atomic file operations",
            "✅ Secure file permissions (0o600)",
            "✅ Memory protection and secure deletion"
        ]
        
        for feature in security_features:
            tk.Label(
                status_frame,
                text=feature,
                font=('Segoe UI', 10),
                bg="#f8f9fa",
                fg="#28a745"
            ).pack(anchor='w', padx=20, pady=2)
        
        tk.Label(status_frame, text="", bg="#f8f9fa").pack(pady=10)
        
        # Storage information
        storage_frame = tk.Frame(parent, bg="#fff3cd", relief='solid', bd=1)
        storage_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            storage_frame,
            text="📁 Where Your API Keys Are Actually Stored",
            font=('Segoe UI', 12, 'bold'),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=(10, 5))
        
        storage_info = self.storage.get_storage_info()
        
        info_items = [
            f"Directory: {storage_info['directory']}",
            f"Encrypted file: {storage_info['encrypted_keys']}",
            f"Salt file: {storage_info['salt_file']}",
            f"Auth file: {storage_info['auth_file']}",
            f"Permissions: {storage_info['permissions']}",
            f"Encryption: {storage_info['encryption']}",
            f"Key derivation: {storage_info['key_derivation']}"
        ]
        
        for item in info_items:
            tk.Label(
                storage_frame,
                text=item,
                font=('Consolas', 9),
                bg="#fff3cd",
                fg="#856404"
            ).pack(anchor='w', padx=15, pady=1)
        
        tk.Label(storage_frame, text="", bg="#fff3cd").pack(pady=5)
    
    def create_bottom_buttons(self):
        """Create bottom action buttons."""
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Button(
            button_frame,
            text="🔄 Refresh",
            command=self.refresh_ui,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            font=('Segoe UI', 10)
        ).pack(side='left')
        
        tk.Button(
            button_frame,
            text="🔒 Lock & Close",
            command=self.secure_close,
            bg='#dc3545',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            font=('Segoe UI', 10, 'bold')
        ).pack(side='right')
    
    def set_api_key(self, provider_id: str):
        """Set API key for provider using secure dialog."""
        try:
            current_key = self.storage.get_api_key(provider_id)
            
            dialog = APIKeyEntryDialog(self.dialog, provider_id, current_key)
            self.dialog.wait_window(dialog.dialog)
            
            if dialog.api_key:
                self.storage.store_api_key(provider_id, dialog.api_key)
                provider_name = provider_config.get_provider(provider_id)['name']
                messagebox.showinfo(
                    "Success", 
                    f"{provider_name} API key encrypted and saved securely!"
                )
                self.refresh_ui()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save API key: {e}")
    
    def remove_api_key(self, provider_id: str):
        """Remove API key for provider."""
        provider_name = provider_config.get_provider(provider_id)['name']
        
        if messagebox.askyesno(
            "Confirm Removal",
            f"Permanently remove encrypted API key for {provider_name}?\n\n"
            "This action cannot be undone."
        ):
            try:
                self.storage.remove_api_key(provider_id)
                messagebox.showinfo("Success", f"API key for {provider_name} securely deleted.")
                self.refresh_ui()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove API key: {e}")
    
    def open_provider_url(self, url: str):
        """Open provider URL in browser."""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            messagebox.showinfo("URL", f"Please visit: {url}")
    
    def refresh_ui(self):
        """Refresh the UI."""
        self.dialog.destroy()
        RealSecureAPIManager(self.parent)
    
    def secure_close(self):
        """Securely close the manager."""
        # Clear sensitive data
        self.storage.secure_shutdown()
        
        # Clear clipboard
        try:
            self.dialog.clipboard_clear()
        except:
            pass
        
        self.dialog.destroy()

def test_real_secure_manager():
    """Test the real secure API manager."""
    root = tk.Tk()
    root.title("Real Secure API Manager Test")
    root.geometry("400x300")
    
    tk.Label(
        root,
        text="🔐 Real Secure API Manager",
        font=('Segoe UI', 16, 'bold')
    ).pack(pady=30)
    
    tk.Label(
        root,
        text="ACTUAL Security • Not Just Secure-Looking GUI",
        font=('Segoe UI', 11),
        fg="#666666"
    ).pack(pady=(0, 20))
    
    tk.Button(
        root,
        text="Open Real Secure Manager",
        command=lambda: RealSecureAPIManager(root),
        font=('Segoe UI', 12, 'bold'),
        bg='#007bff',
        fg='white',
        padx=25,
        pady=12
    ).pack(pady=20)
    
    tk.Label(
        root,
        text="Requires: pip install cryptography",
        font=('Segoe UI', 9),
        fg="#dc3545"
    ).pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_real_secure_manager()
