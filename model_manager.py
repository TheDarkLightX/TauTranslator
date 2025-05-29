#!/usr/bin/env python3
"""
Model Manager for TauTranslatorOmega
===================================

Handles downloading, installing, and managing AI models including:
- Gemma 3 4B from Hugging Face
- LMQL integration
- Model switching and configuration
- Iterative feedback loop
"""

import sys
import os
import json
import threading
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Callable
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# Try to import requests, install if missing
try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'])
    import requests

class ModelManager:
    """Manages AI models for TauTranslatorOmega."""
    
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.config_file = self.models_dir / "model_config.json"
        self.feedback_file = self.models_dir / "feedback_data.json"
        
        self.available_models = {
            "gemma3_4b": {
                "name": "Gemma 3 4B",
                "description": "Google's Gemma 3 4B model from Hugging Face",
                "size": "8.5 GB",
                "url": "google/gemma-2-2b-it",  # Using 2B for faster download
                "type": "huggingface",
                "installed": False,
                "path": None
            },
            "pattern_based": {
                "name": "Pattern-based Translator",
                "description": "Rule-based pattern matching translator",
                "size": "< 1 MB",
                "type": "builtin",
                "installed": True,
                "path": "builtin"
            }
        }
        
        self.current_model = "pattern_based"
        self.load_config()
        
    def load_config(self):
        """Load model configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.current_model = config.get('current_model', 'pattern_based')
                    
                    # Update model status
                    for model_id, model_config in config.get('models', {}).items():
                        if model_id in self.available_models:
                            self.available_models[model_id].update(model_config)
            except Exception as e:
                self.log_status(f"Failed to load config: {e}")
    
    def save_config(self):
        """Save model configuration."""
        config = {
            'current_model': self.current_model,
            'models': self.available_models,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.log_status(f"Failed to save config: {e}")
    
    def log_status(self, message: str):
        """Log status message."""
        print(f"[ModelManager] {message}")
        if self.status_callback:
            self.status_callback(message)
    
    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are installed."""
        dependencies = {
            'transformers': False,
            'torch': False,
            'lmql': False,
            'huggingface_hub': False
        }
        
        for package in dependencies:
            try:
                __import__(package)
                dependencies[package] = True
            except ImportError:
                dependencies[package] = False
        
        return dependencies
    
    def install_dependencies(self, progress_callback: Optional[Callable] = None):
        """Install required dependencies."""
        packages = [
            'torch',  # Install torch first
            'transformers',
            'huggingface-hub',
            'accelerate'
            # Skip lmql for now as it can be complex
        ]

        def install():
            try:
                total_packages = len(packages)

                for i, package in enumerate(packages):
                    if progress_callback:
                        progress_callback(f"Installing {package}... ({i+1}/{total_packages})", i / total_packages)

                    # Use --user flag to avoid permission issues
                    cmd = [sys.executable, '-m', 'pip', 'install', '--user', package]

                    result = subprocess.run(cmd, capture_output=True, text=True)

                    if result.returncode != 0:
                        # Try without --user flag
                        cmd = [sys.executable, '-m', 'pip', 'install', package]
                        result = subprocess.run(cmd, capture_output=True, text=True)

                        if result.returncode != 0:
                            error_msg = f"Failed to install {package}:\n{result.stderr}\n{result.stdout}"
                            if progress_callback:
                                progress_callback(error_msg, -1)
                            return

                    if progress_callback:
                        progress_callback(f"✅ {package} installed successfully", (i + 1) / total_packages)

                if progress_callback:
                    progress_callback("🎉 All dependencies installed successfully!", 1.0)

            except Exception as e:
                if progress_callback:
                    progress_callback(f"Installation failed: {str(e)}", -1)

        threading.Thread(target=install, daemon=True).start()
    
    def download_gemma3(self, progress_callback: Optional[Callable] = None):
        """Download Gemma 3 model from Hugging Face."""
        def download():
            try:
                if progress_callback:
                    progress_callback("🔍 Checking dependencies...", 0.1)

                # Check dependencies
                deps = self.check_dependencies()
                missing = [k for k, v in deps.items() if not v if k in ['transformers', 'huggingface_hub']]

                if missing:
                    error_msg = f"❌ Missing required dependencies: {', '.join(missing)}\nPlease install them first using the Dependencies tab."
                    if progress_callback:
                        progress_callback(error_msg, -1)
                    return

                if progress_callback:
                    progress_callback("📦 Importing Hugging Face libraries...", 0.2)

                try:
                    from huggingface_hub import snapshot_download
                except ImportError as e:
                    error_msg = f"❌ Failed to import huggingface_hub: {e}\nPlease install dependencies first."
                    if progress_callback:
                        progress_callback(error_msg, -1)
                    return

                model_id = self.available_models["gemma3_4b"]["url"]
                model_path = self.models_dir / "gemma3_4b"
                model_path.mkdir(exist_ok=True)

                if progress_callback:
                    progress_callback(f"⬇️ Downloading {model_id}...\nThis may take several minutes...", 0.3)

                try:
                    # Download model with progress
                    downloaded_path = snapshot_download(
                        repo_id=model_id,
                        local_dir=str(model_path),
                        local_dir_use_symlinks=False,
                        resume_download=True  # Allow resuming interrupted downloads
                    )

                    # Update model config
                    self.available_models["gemma3_4b"]["installed"] = True
                    self.available_models["gemma3_4b"]["path"] = str(downloaded_path)
                    self.save_config()

                    if progress_callback:
                        progress_callback("🎉 Gemma 3 model downloaded successfully!", 1.0)

                except Exception as download_error:
                    error_msg = f"❌ Download failed: {str(download_error)}\n\nTips:\n- Check internet connection\n- Ensure sufficient disk space (~8GB)\n- Try again later if servers are busy"
                    if progress_callback:
                        progress_callback(error_msg, -1)

            except Exception as e:
                error_msg = f"❌ Unexpected error: {str(e)}"
                if progress_callback:
                    progress_callback(error_msg, -1)

        threading.Thread(target=download, daemon=True).start()
    
    def load_gemma3_model(self):
        """Load Gemma 3 model for inference."""
        try:
            if not self.available_models["gemma3_4b"]["installed"]:
                raise Exception("Gemma 3 model not installed")
            
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            model_path = self.available_models["gemma3_4b"]["path"]
            
            self.log_status("Loading Gemma 3 tokenizer...")
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            
            self.log_status("Loading Gemma 3 model...")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            self.current_model = "gemma3_4b"
            self.save_config()
            
            return model, tokenizer
            
        except Exception as e:
            self.log_status(f"Failed to load Gemma 3: {e}")
            return None, None
    
    def setup_lmql(self):
        """Setup LMQL for advanced querying."""
        try:
            import lmql
            
            # LMQL query template for Tau translation
            lmql_template = '''
            @lmql.query
            def translate_tau_to_english(tau_code: str):
                """Translate Tau language code to natural English."""
                """
                You are an expert in Tau language translation. 
                Translate the following Tau language code to clear, natural English:
                
                Tau Code: {tau_code}
                
                Translation Rules:
                - i1[t], i2[t] should become "input 1 at time t", "input 2 at time t"
                - & should become "AND"
                - | should become "OR" 
                - + should become "XOR" in boolean context, "plus" in arithmetic
                - = should become "equals"
                - > should become "is greater than"
                - Function definitions should be clear and descriptive
                
                Natural English Translation:
                """[TRANSLATION]
                
                return TRANSLATION
            '''
            
            return lmql_template
            
        except ImportError:
            self.log_status("LMQL not available. Install with: pip install lmql")
            return None
        except Exception as e:
            self.log_status(f"LMQL setup failed: {e}")
            return None
    
    def collect_feedback(self, input_text: str, output_text: str, rating: int, comments: str = ""):
        """Collect user feedback for iterative improvement."""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": self.current_model,
            "input": input_text,
            "output": output_text,
            "rating": rating,  # 1-5 scale
            "comments": comments,
            "session_id": id(self)  # Simple session tracking
        }
        
        # Load existing feedback
        feedback_data = []
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, 'r') as f:
                    feedback_data = json.load(f)
            except Exception:
                feedback_data = []
        
        # Add new feedback
        feedback_data.append(feedback_entry)
        
        # Save feedback
        try:
            with open(self.feedback_file, 'w') as f:
                json.dump(feedback_data, f, indent=2)
            
            self.log_status(f"Feedback collected (Rating: {rating}/5)")
            
        except Exception as e:
            self.log_status(f"Failed to save feedback: {e}")
    
    def analyze_feedback(self) -> Dict:
        """Analyze collected feedback for insights."""
        if not self.feedback_file.exists():
            return {"total": 0, "average_rating": 0, "insights": []}
        
        try:
            with open(self.feedback_file, 'r') as f:
                feedback_data = json.load(f)
            
            if not feedback_data:
                return {"total": 0, "average_rating": 0, "insights": []}
            
            total = len(feedback_data)
            ratings = [entry["rating"] for entry in feedback_data]
            average_rating = sum(ratings) / len(ratings)
            
            # Model performance comparison
            model_ratings = {}
            for entry in feedback_data:
                model = entry["model"]
                if model not in model_ratings:
                    model_ratings[model] = []
                model_ratings[model].append(entry["rating"])
            
            insights = []
            for model, ratings in model_ratings.items():
                avg = sum(ratings) / len(ratings)
                insights.append(f"{model}: {avg:.1f}/5 ({len(ratings)} samples)")
            
            return {
                "total": total,
                "average_rating": average_rating,
                "model_performance": model_ratings,
                "insights": insights
            }
            
        except Exception as e:
            self.log_status(f"Failed to analyze feedback: {e}")
            return {"total": 0, "average_rating": 0, "insights": []}
    
    def get_model_status(self) -> Dict:
        """Get current model status."""
        return {
            "current": self.current_model,
            "available": self.available_models,
            "dependencies": self.check_dependencies()
        }

class ModelManagerDialog:
    """GUI dialog for model management."""
    
    def __init__(self, parent, model_manager: ModelManager):
        self.parent = parent
        self.model_manager = model_manager
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Model Manager")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_ui()
    
    def create_ui(self):
        """Create the model manager UI."""
        # Notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Models tab
        models_frame = ttk.Frame(notebook)
        notebook.add(models_frame, text="Models")
        self.create_models_tab(models_frame)
        
        # Dependencies tab
        deps_frame = ttk.Frame(notebook)
        notebook.add(deps_frame, text="Dependencies")
        self.create_dependencies_tab(deps_frame)
        
        # Feedback tab
        feedback_frame = ttk.Frame(notebook)
        notebook.add(feedback_frame, text="Feedback")
        self.create_feedback_tab(feedback_frame)
    
    def create_models_tab(self, parent):
        """Create models management tab."""
        # Available models
        ttk.Label(parent, text="Available Models:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        # Models listbox
        models_frame = ttk.Frame(parent)
        models_frame.pack(fill='both', expand=True, pady=5)
        
        self.models_listbox = tk.Listbox(models_frame, height=8)
        self.models_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(models_frame, orient='vertical', command=self.models_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.models_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate models
        self.refresh_models_list()
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(buttons_frame, text="Download Gemma 3", command=self.download_gemma3).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Load Model", command=self.load_selected_model).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Refresh", command=self.refresh_models_list).pack(side='left', padx=5)
        
        # Status
        self.status_label = ttk.Label(parent, text="Ready")
        self.status_label.pack(anchor='w', pady=5)
    
    def create_dependencies_tab(self, parent):
        """Create dependencies tab."""
        ttk.Label(parent, text="Required Dependencies:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        # Dependencies list
        self.deps_text = tk.Text(parent, height=15, width=60)
        self.deps_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(buttons_frame, text="Check Dependencies", command=self.check_dependencies).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Install All", command=self.install_dependencies).pack(side='left', padx=5)
        
        self.check_dependencies()
    
    def create_feedback_tab(self, parent):
        """Create feedback analysis tab."""
        ttk.Label(parent, text="Translation Feedback Analysis:", font=('TkDefaultFont', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        # Feedback display
        self.feedback_text = tk.Text(parent, height=15, width=60)
        self.feedback_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.pack(fill='x', pady=10)
        
        ttk.Button(buttons_frame, text="Analyze Feedback", command=self.analyze_feedback).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="Export Data", command=self.export_feedback).pack(side='left', padx=5)
        
        self.analyze_feedback()
    
    def refresh_models_list(self):
        """Refresh the models list."""
        self.models_listbox.delete(0, tk.END)
        
        for model_id, model_info in self.model_manager.available_models.items():
            status = "✅ Installed" if model_info["installed"] else "❌ Not Installed"
            current = "🔥 Current" if model_id == self.model_manager.current_model else ""
            
            display_text = f"{model_info['name']} - {model_info['size']} - {status} {current}"
            self.models_listbox.insert(tk.END, display_text)
    
    def download_gemma3(self):
        """Download Gemma 3 model with progress."""
        def progress_callback(message, progress):
            self.status_label.config(text=message)
            if progress == 1.0:
                self.refresh_models_list()
            elif progress == -1:
                messagebox.showerror("Error", message)
        
        self.model_manager.download_gemma3(progress_callback)
    
    def load_selected_model(self):
        """Load the selected model."""
        selection = self.models_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a model")
            return
        
        model_ids = list(self.model_manager.available_models.keys())
        model_id = model_ids[selection[0]]
        
        if model_id == "gemma3_4b":
            self.status_label.config(text="Loading Gemma 3...")
            model, tokenizer = self.model_manager.load_gemma3_model()
            if model:
                self.status_label.config(text="Gemma 3 loaded successfully!")
                self.refresh_models_list()
            else:
                self.status_label.config(text="Failed to load Gemma 3")
        else:
            self.model_manager.current_model = model_id
            self.model_manager.save_config()
            self.status_label.config(text=f"Switched to {model_id}")
            self.refresh_models_list()
    
    def check_dependencies(self):
        """Check and display dependencies."""
        deps = self.model_manager.check_dependencies()
        
        self.deps_text.delete('1.0', tk.END)
        self.deps_text.insert('1.0', "Dependency Status:\\n\\n")
        
        for package, installed in deps.items():
            status = "✅ Installed" if installed else "❌ Missing"
            self.deps_text.insert(tk.END, f"{package}: {status}\\n")
        
        missing = [k for k, v in deps.items() if not v]
        if missing:
            self.deps_text.insert(tk.END, f"\\nMissing packages: {', '.join(missing)}\\n")
            self.deps_text.insert(tk.END, "Click 'Install All' to install missing dependencies.\\n")
        else:
            self.deps_text.insert(tk.END, "\\nAll dependencies are installed! ✅\\n")
    
    def install_dependencies(self):
        """Install dependencies with progress."""
        def progress_callback(message, progress):
            self.deps_text.insert(tk.END, f"{message}\\n")
            self.deps_text.see(tk.END)
            if progress == 1.0:
                self.check_dependencies()
            elif progress == -1:
                messagebox.showerror("Error", message)
        
        self.model_manager.install_dependencies(progress_callback)
    
    def analyze_feedback(self):
        """Analyze and display feedback."""
        analysis = self.model_manager.analyze_feedback()
        
        self.feedback_text.delete('1.0', tk.END)
        self.feedback_text.insert('1.0', "Feedback Analysis:\\n\\n")
        
        self.feedback_text.insert(tk.END, f"Total Feedback Entries: {analysis['total']}\\n")
        self.feedback_text.insert(tk.END, f"Average Rating: {analysis['average_rating']:.1f}/5\\n\\n")
        
        if analysis['insights']:
            self.feedback_text.insert(tk.END, "Model Performance:\\n")
            for insight in analysis['insights']:
                self.feedback_text.insert(tk.END, f"• {insight}\\n")
        else:
            self.feedback_text.insert(tk.END, "No feedback data available yet.\\n")
            self.feedback_text.insert(tk.END, "Use the application and provide ratings to see analysis here.\\n")
    
    def export_feedback(self):
        """Export feedback data."""
        messagebox.showinfo("Export", "Feedback export feature coming soon!")

def main():
    """Test the model manager."""
    root = tk.Tk()
    root.title("Model Manager Test")
    
    manager = ModelManager()
    dialog = ModelManagerDialog(root, manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()
