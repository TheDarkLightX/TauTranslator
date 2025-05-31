#!/usr/bin/env python3
"""
API Key Entry Dialog
===================

Secure dialog for entering API keys with clear indication of where they go.
"""

import tkinter as tk
from tkinter import messagebox
from provider_config import provider_config

class APIKeyEntryDialog:
    """Secure API key entry dialog."""
    
    def __init__(self, parent, provider_id: str, current_key: str = ""):
        self.parent = parent
        self.provider_id = provider_id
        self.current_key = current_key
        self.api_key = None
        
        # Get provider info
        self.provider_info = provider_config.get_provider(provider_id)
        if not self.provider_info:
            raise ValueError(f"Unknown provider: {provider_id}")
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Set {self.provider_info['name']} API Key")

        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Calculate responsive size (minimum 600x550, max 70% of screen)
        width = max(600, min(800, int(screen_width * 0.5)))
        height = max(550, min(700, int(screen_height * 0.7)))

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
        self.dialog.minsize(600, 550)
        
        self.create_ui()
    
    def create_ui(self):
        """Create the API key entry UI."""
        # Header
        self.create_header()
        
        # Main content
        main_frame = tk.Frame(self.dialog, bg="white")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Provider info
        self.create_provider_info(main_frame)
        
        # Security notice
        self.create_security_notice(main_frame)
        
        # API key entry
        self.create_key_entry(main_frame)
        
        # Storage info
        self.create_storage_info(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.save_key())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def create_header(self):
        """Create dialog header."""
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=70)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        title_frame = tk.Frame(header_frame, bg="#2c3e50")
        title_frame.pack(expand=True)
        
        tk.Label(
            title_frame,
            text=f"🔐 {self.provider_info['name']} API Key",
            font=('Segoe UI', 16, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack()
        
        if self.provider_info.get('recommended'):
            tk.Label(
                title_frame,
                text="⭐ RECOMMENDED PROVIDER",
                font=('Segoe UI', 10),
                bg="#2c3e50",
                fg="#ffd700"
            ).pack()
    
    def create_provider_info(self, parent):
        """Create provider information section."""
        info_frame = tk.Frame(parent, bg="#f8f9fa", relief='solid', bd=1)
        info_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            info_frame,
            text=self.provider_info['description'],
            font=('Segoe UI', 11, 'bold'),
            bg="#f8f9fa",
            fg="#2c3e50"
        ).pack(pady=(10, 5))
        
        # Benefits
        if 'benefits' in self.provider_info:
            for benefit in self.provider_info['benefits']:
                tk.Label(
                    info_frame,
                    text=f"• {benefit}",
                    font=('Segoe UI', 9),
                    bg="#f8f9fa",
                    fg="#495057"
                ).pack(anchor='w', padx=20, pady=1)
        
        # Get API key link
        link_frame = tk.Frame(info_frame, bg="#f8f9fa")
        link_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        tk.Button(
            link_frame,
            text=f"🌐 Get {self.provider_info['name']} API Key",
            command=self.open_provider_url,
            bg='#17a2b8',
            fg='white',
            relief='flat',
            padx=15,
            pady=6,
            font=('Segoe UI', 9, 'bold')
        ).pack(side='right')
    
    def create_security_notice(self, parent):
        """Create security notice section."""
        security_frame = tk.Frame(parent, bg="#d1ecf1", relief='solid', bd=1)
        security_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            security_frame,
            text="🔒 Security Information",
            font=('Segoe UI', 10, 'bold'),
            bg="#d1ecf1",
            fg="#0c5460"
        ).pack(pady=(8, 5))
        
        security_info = [
            "Your API key will be encrypted with AES-256-GCM",
            "Keys are stored locally on your machine only",
            "Never transmitted to external servers",
            "Protected by your master password"
        ]
        
        for info in security_info:
            tk.Label(
                security_frame,
                text=f"• {info}",
                font=('Segoe UI', 9),
                bg="#d1ecf1",
                fg="#0c5460"
            ).pack(anchor='w', padx=20, pady=1)
        
        tk.Label(security_frame, text="", bg="#d1ecf1").pack(pady=3)
    
    def create_key_entry(self, parent):
        """Create API key entry section."""
        # Format info
        tk.Label(
            parent,
            text=f"Expected format: {self.provider_info['example']}",
            font=('Segoe UI', 9, 'italic'),
            bg="white",
            fg="#666666"
        ).pack(anchor='w', pady=(0, 5))
        
        # API key label
        tk.Label(
            parent,
            text="API Key:",
            font=('Segoe UI', 10, 'bold'),
            bg="white"
        ).pack(anchor='w')
        
        # API key entry
        self.key_var = tk.StringVar(value=self.current_key)
        self.key_entry = tk.Entry(
            parent,
            textvariable=self.key_var,
            show="*",
            font=('Consolas', 10),
            width=70
        )
        self.key_entry.pack(fill='x', pady=(5, 10))
        self.key_entry.focus()
        
        # Show/hide toggle
        self.show_key = tk.BooleanVar()
        tk.Checkbutton(
            parent,
            text="Show API key",
            variable=self.show_key,
            command=self.toggle_key_visibility,
            bg="white",
            font=('Segoe UI', 9)
        ).pack(anchor='w', pady=(0, 15))
    
    def create_storage_info(self, parent):
        """Create storage information section."""
        storage_frame = tk.Frame(parent, bg="#fff3cd", relief='solid', bd=1)
        storage_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            storage_frame,
            text="📁 Where Your API Key Will Be Stored",
            font=('Segoe UI', 10, 'bold'),
            bg="#fff3cd",
            fg="#856404"
        ).pack(pady=(8, 5))
        
        # Import here to avoid circular imports
        from secure_core import SecureStorage
        storage = SecureStorage()
        storage_info = storage.get_storage_info()
        
        info_text = f"Location: {storage_info['directory']}\n"
        info_text += f"File: {storage_info['encrypted_keys']}\n"
        info_text += f"Encryption: {storage_info['encryption']}\n"
        info_text += f"Permissions: {storage_info['permissions']}"
        
        tk.Label(
            storage_frame,
            text=info_text,
            font=('Consolas', 8),
            bg="#fff3cd",
            fg="#856404",
            justify='left'
        ).pack(anchor='w', padx=15, pady=(0, 8))
    
    def create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(fill='x')
        
        # Cancel button
        tk.Button(
            button_frame,
            text="Cancel",
            command=self.cancel,
            bg='#6c757d',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            font=('Segoe UI', 10)
        ).pack(side='right', padx=(10, 0))
        
        # Save button
        tk.Button(
            button_frame,
            text="🔐 Save Encrypted",
            command=self.save_key,
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            font=('Segoe UI', 10, 'bold')
        ).pack(side='right')
    
    def toggle_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key.get():
            self.key_entry.config(show="")
        else:
            self.key_entry.config(show="*")
    
    def open_provider_url(self):
        """Open provider URL in browser."""
        try:
            import webbrowser
            webbrowser.open(self.provider_info['url'])
        except Exception:
            messagebox.showinfo("URL", f"Please visit: {self.provider_info['url']}")
    
    def save_key(self):
        """Save the API key."""
        api_key = self.key_var.get().strip()
        
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        # Validate format
        error = provider_config.get_validation_error(self.provider_id, api_key)
        if error:
            messagebox.showerror("Invalid API Key", error)
            return
        
        self.api_key = api_key
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel dialog."""
        self.api_key = None
        self.dialog.destroy()

def test_api_key_dialog():
    """Test the API key entry dialog."""
    root = tk.Tk()
    root.title("API Key Dialog Test")
    root.geometry("300x200")
    
    def test_openrouter():
        dialog = APIKeyEntryDialog(root, "openrouter")
        root.wait_window(dialog.dialog)
        if dialog.api_key:
            messagebox.showinfo("Result", f"Key entered: {dialog.api_key[:10]}...")
    
    def test_openai():
        dialog = APIKeyEntryDialog(root, "openai", "sk-existing-key")
        root.wait_window(dialog.dialog)
        if dialog.api_key:
            messagebox.showinfo("Result", f"Key entered: {dialog.api_key[:10]}...")
    
    tk.Button(root, text="Test OpenRouter", command=test_openrouter).pack(pady=10)
    tk.Button(root, text="Test OpenAI", command=test_openai).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_api_key_dialog()
