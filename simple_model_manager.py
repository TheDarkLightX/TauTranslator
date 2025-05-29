#!/usr/bin/env python3
"""
Simple Model Manager for TauTranslatorOmega
==========================================

A simplified, working model manager that focuses on core functionality:
- Dependency checking and installation
- Basic model management
- Simple UI that actually works
"""

import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
import json

class SimpleModelManager:
    """Simplified model manager that actually works."""
    
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.required_packages = [
            'torch',
            'transformers', 
            'huggingface-hub',
            'accelerate'
        ]
        
        self.current_model = "pattern_based"
    
    def check_package(self, package_name):
        """Check if a package is installed."""
        try:
            __import__(package_name.replace('-', '_'))
            return True
        except ImportError:
            return False
    
    def install_package(self, package_name, progress_callback=None):
        """Install a single package."""
        try:
            if progress_callback:
                progress_callback(f"Installing {package_name}...")
            
            # Try with --user first
            cmd = [sys.executable, '-m', 'pip', 'install', '--user', package_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                # Try without --user
                cmd = [sys.executable, '-m', 'pip', 'install', package_name]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                if progress_callback:
                    progress_callback(f"✅ {package_name} installed successfully")
                return True
            else:
                if progress_callback:
                    progress_callback(f"❌ Failed to install {package_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            if progress_callback:
                progress_callback(f"⏰ Timeout installing {package_name}")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"💥 Error installing {package_name}: {e}")
            return False
    
    def install_all_dependencies(self, progress_callback=None):
        """Install all required dependencies."""
        def install():
            success_count = 0
            total = len(self.required_packages)
            
            for i, package in enumerate(self.required_packages):
                if progress_callback:
                    progress_callback(f"Installing {package} ({i+1}/{total})...")
                
                if self.install_package(package, progress_callback):
                    success_count += 1
                else:
                    if progress_callback:
                        progress_callback(f"❌ Failed to install {package}")
            
            if progress_callback:
                if success_count == total:
                    progress_callback(f"🎉 All {total} packages installed successfully!")
                else:
                    progress_callback(f"⚠️ Installed {success_count}/{total} packages")
        
        threading.Thread(target=install, daemon=True).start()
    
    def download_small_model(self, progress_callback=None):
        """Download a small test model."""
        def download():
            try:
                if progress_callback:
                    progress_callback("🔍 Checking dependencies...")
                
                if not self.check_package('huggingface_hub'):
                    if progress_callback:
                        progress_callback("❌ huggingface-hub not installed. Please install dependencies first.")
                    return
                
                if progress_callback:
                    progress_callback("📦 Importing libraries...")
                
                from huggingface_hub import snapshot_download
                
                # Use a very small model for testing
                model_id = "microsoft/DialoGPT-small"  # Much smaller than Gemma
                model_path = self.models_dir / "test_model"
                
                if progress_callback:
                    progress_callback(f"⬇️ Downloading {model_id}...")
                
                downloaded_path = snapshot_download(
                    repo_id=model_id,
                    local_dir=str(model_path),
                    local_dir_use_symlinks=False
                )
                
                if progress_callback:
                    progress_callback(f"✅ Model downloaded to {downloaded_path}")
                
            except Exception as e:
                if progress_callback:
                    progress_callback(f"❌ Download failed: {e}")
        
        threading.Thread(target=download, daemon=True).start()

class SimpleModelManagerDialog:
    """Simple dialog for model management."""
    
    def __init__(self, parent):
        self.parent = parent
        self.manager = SimpleModelManager()
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Simple Model Manager")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        
        self.create_ui()
    
    def create_ui(self):
        """Create the UI."""
        # Title
        title_label = tk.Label(
            self.dialog,
            text="🤖 Simple Model Manager",
            font=('TkDefaultFont', 14, 'bold')
        )
        title_label.pack(pady=10)
        
        # Status display
        self.status_text = scrolledtext.ScrolledText(
            self.dialog,
            height=15,
            width=60,
            wrap=tk.WORD
        )
        self.status_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            button_frame,
            text="Check Dependencies",
            command=self.check_dependencies,
            bg='lightblue'
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Install Dependencies",
            command=self.install_dependencies,
            bg='lightgreen'
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Download Test Model",
            command=self.download_model,
            bg='lightyellow'
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy,
            bg='lightcoral'
        ).pack(side='right', padx=5)
        
        # Initial check
        self.check_dependencies()
    
    def log_message(self, message):
        """Add message to status display."""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.dialog.update()
    
    def check_dependencies(self):
        """Check dependency status."""
        self.log_message("🔍 Checking Dependencies...")
        self.log_message("-" * 30)
        
        for package in self.manager.required_packages:
            if self.manager.check_package(package):
                self.log_message(f"✅ {package}: Installed")
            else:
                self.log_message(f"❌ {package}: Missing")
        
        self.log_message("-" * 30)
        self.log_message("Check complete.\n")
    
    def install_dependencies(self):
        """Install dependencies."""
        self.log_message("📦 Starting dependency installation...")
        self.log_message("This may take several minutes...\n")
        
        def progress_callback(message):
            self.dialog.after(0, lambda: self.log_message(message))
        
        self.manager.install_all_dependencies(progress_callback)
    
    def download_model(self):
        """Download test model."""
        self.log_message("⬇️ Starting model download...")
        self.log_message("Downloading small test model...\n")
        
        def progress_callback(message):
            self.dialog.after(0, lambda: self.log_message(message))
        
        self.manager.download_small_model(progress_callback)

def test_simple_manager():
    """Test the simple model manager."""
    print("🧪 Testing Simple Model Manager")
    
    root = tk.Tk()
    root.title("Model Manager Test")
    root.geometry("300x200")
    
    # Test button
    test_button = tk.Button(
        root,
        text="Open Model Manager",
        command=lambda: SimpleModelManagerDialog(root),
        font=('TkDefaultFont', 12),
        bg='lightblue',
        padx=20,
        pady=10
    )
    test_button.pack(expand=True)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Click the button to open the Model Manager\nand test dependency installation",
        justify='center'
    )
    instructions.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    test_simple_manager()
