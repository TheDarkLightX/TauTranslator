#!/usr/bin/env python3
"""
Secure Password Dialog
=====================

Secure password input with real validation.
"""

import tkinter as tk
from tkinter import messagebox

class SecurePasswordDialog:
    """Secure password input dialog."""
    
    def __init__(self, parent, title="Enter Master Password", is_new=False):
        self.parent = parent
        self.password = None
        self.is_new = is_new
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)

        # Get screen dimensions
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()

        # Calculate responsive size (minimum 500x500, max 80% of screen)
        width = max(500, min(600, int(screen_width * 0.4)))
        height = max(500, min(650, int(screen_height * 0.6)))

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
        self.dialog.minsize(500, 500)
        
        self.create_ui()
    
    def create_ui(self):
        """Create password input UI."""
        # Header
        header_frame = tk.Frame(self.dialog, bg="#2c3e50", height=60)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🔐 Secure Authentication",
            font=('Segoe UI', 16, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.dialog, bg="white")
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Instructions
        if self.is_new:
            instruction_text = "Create a strong master password to encrypt your API keys:"
        else:
            instruction_text = "Enter your master password to access encrypted API keys:"
        
        tk.Label(
            main_frame,
            text=instruction_text,
            font=('Segoe UI', 11),
            bg="white",
            wraplength=400,
            justify='left'
        ).pack(pady=(0, 15))
        
        # Password requirements (for new passwords)
        if self.is_new:
            self.create_requirements_section(main_frame)
        
        # Password entry section
        self.create_password_section(main_frame)
        
        # Buttons
        self.create_buttons(main_frame)
        
        # Bind keys
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
    
    def create_requirements_section(self, parent):
        """Create password requirements section."""
        req_frame = tk.Frame(parent, bg="#f8f9fa", relief='solid', bd=1)
        req_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            req_frame,
            text="Password Requirements:",
            font=('Segoe UI', 10, 'bold'),
            bg="#f8f9fa"
        ).pack(anchor='w', padx=10, pady=(10, 5))
        
        requirements = [
            "• At least 12 characters long",
            "• Mix of uppercase and lowercase letters", 
            "• Include numbers and special characters",
            "• Avoid common words or patterns"
        ]
        
        for req in requirements:
            tk.Label(
                req_frame,
                text=req,
                font=('Segoe UI', 9),
                bg="#f8f9fa",
                fg="#666666"
            ).pack(anchor='w', padx=20, pady=1)
        
        tk.Label(req_frame, text="", bg="#f8f9fa").pack(pady=5)
    
    def create_password_section(self, parent):
        """Create password input section."""
        # Password label
        tk.Label(
            parent,
            text="Master Password:",
            font=('Segoe UI', 10, 'bold'),
            bg="white"
        ).pack(anchor='w')
        
        # Password entry
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            parent,
            textvariable=self.password_var,
            show="*",
            font=('Segoe UI', 11),
            width=50
        )
        self.password_entry.pack(fill='x', pady=(5, 10))
        self.password_entry.focus()
        
        # Show/hide toggle
        self.show_password = tk.BooleanVar()
        show_check = tk.Checkbutton(
            parent,
            text="Show password",
            variable=self.show_password,
            command=self.toggle_password_visibility,
            bg="white",
            font=('Segoe UI', 9)
        )
        show_check.pack(anchor='w', pady=(0, 15))
        
        # Security notice
        if self.is_new:
            notice_frame = tk.Frame(parent, bg="#fff3cd", relief='solid', bd=1)
            notice_frame.pack(fill='x', pady=(0, 15))
            
            tk.Label(
                notice_frame,
                text="⚠️ Important: Remember this password! There is no recovery option.",
                font=('Segoe UI', 9, 'bold'),
                bg="#fff3cd",
                fg="#856404"
            ).pack(pady=8)
    
    def create_buttons(self, parent):
        """Create dialog buttons."""
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(fill='x', pady=(10, 0))
        
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
        
        # OK button
        ok_text = "Create" if self.is_new else "Unlock"
        tk.Button(
            button_frame,
            text=ok_text,
            command=self.ok,
            bg='#28a745',
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            font=('Segoe UI', 10, 'bold')
        ).pack(side='right')
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_password.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def validate_password_strength(self, password: str) -> tuple:
        """Validate password strength."""
        if len(password) < 12:
            return False, "Password must be at least 12 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letters"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain lowercase letters"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain numbers"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain special characters"
        
        # Check for common patterns
        common_patterns = ["123", "abc", "password", "qwerty"]
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                return False, f"Password should not contain common patterns like '{pattern}'"
        
        return True, "Password is strong"
    
    def ok(self):
        """Handle OK button."""
        password = self.password_var.get()
        
        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return
        
        if self.is_new:
            valid, message = self.validate_password_strength(password)
            if not valid:
                messagebox.showerror("Weak Password", message)
                return
        
        self.password = password
        self.dialog.destroy()
    
    def cancel(self):
        """Handle Cancel button."""
        self.password = None
        self.dialog.destroy()

def test_password_dialog():
    """Test the password dialog."""
    root = tk.Tk()
    root.title("Password Dialog Test")
    root.geometry("300x200")
    
    def test_new():
        dialog = SecurePasswordDialog(root, "Create Password", is_new=True)
        root.wait_window(dialog.dialog)
        if dialog.password:
            messagebox.showinfo("Result", f"Password created: {len(dialog.password)} chars")
    
    def test_existing():
        dialog = SecurePasswordDialog(root, "Enter Password", is_new=False)
        root.wait_window(dialog.dialog)
        if dialog.password:
            messagebox.showinfo("Result", f"Password entered: {len(dialog.password)} chars")
    
    tk.Button(root, text="Test New Password", command=test_new).pack(pady=10)
    tk.Button(root, text="Test Existing Password", command=test_existing).pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_password_dialog()
