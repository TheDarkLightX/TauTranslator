#!/usr/bin/env python3
"""
NLP GUI Demo
============

Simple GUI demonstration of the integrated NLP system.
Shows translation with confidence scores and NLP features.

Author: DarklightX (Dana Edwards)
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import requests
import threading
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Try to import NLP system directly
try:
    from nlp.integrated_nlp_system import NLPIntegrationAPI
    NLP_AVAILABLE = True
except:
    NLP_AVAILABLE = False


class NLPTranslatorGUI:
    """GUI for demonstrating NLP-enhanced translation."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("TauTranslator - NLP Enhanced Demo")
        self.root.geometry("1200x800")
        
        # Initialize NLP if available
        self.nlp_api = NLPIntegrationAPI() if NLP_AVAILABLE else None
        self.backend_url = "http://localhost:8000"
        
        # Create UI
        self.create_widgets()
        self.check_backend_status()
        
    def create_widgets(self):
        """Create the GUI widgets."""
        # Header
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.pack(fill=tk.X)
        
        ttk.Label(
            header_frame, 
            text="TauTranslator NLP Demo", 
            font=("Arial", 20, "bold")
        ).pack()
        
        ttk.Label(
            header_frame,
            text="Natural Language Processing Enhanced Translation",
            font=("Arial", 12)
        ).pack()
        
        # Status bar
        self.status_frame = ttk.Frame(self.root, padding="5")
        self.status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Status: Checking services...",
            font=("Arial", 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Main content
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Input
        left_frame = ttk.LabelFrame(main_frame, text="Input (TCE/Natural Language)", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.input_text = scrolledtext.ScrolledText(
            left_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=("Consolas", 12)
        )
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # Insert example text
        self.input_text.insert("1.0", "Always x is greater than 5")
        
        # Right panel - Output
        right_frame = ttk.LabelFrame(main_frame, text="Output (Tau Language)", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.output_text = scrolledtext.ScrolledText(
            right_frame,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=("Consolas", 12)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # Translation options
        options_frame = ttk.LabelFrame(control_frame, text="Options", padding="5")
        options_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.use_nlp_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Use NLP Enhancement",
            variable=self.use_nlp_var
        ).pack(side=tk.LEFT, padx=5)
        
        self.show_details_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Show Details",
            variable=self.show_details_var
        ).pack(side=tk.LEFT, padx=5)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.translate_btn = ttk.Button(
            button_frame,
            text="Translate →",
            command=self.translate,
            style="Accent.TButton"
        )
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Examples",
            command=self.show_examples
        ).pack(side=tk.LEFT, padx=5)
        
        # Results panel
        results_frame = ttk.LabelFrame(self.root, text="NLP Analysis Results", padding="10")
        results_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Confidence meter
        conf_frame = ttk.Frame(results_frame)
        conf_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(conf_frame, text="Confidence:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.confidence_var = tk.DoubleVar(value=0.0)
        self.confidence_bar = ttk.Progressbar(
            conf_frame,
            length=200,
            mode='determinate',
            variable=self.confidence_var
        )
        self.confidence_bar.pack(side=tk.LEFT, padx=(0, 10))
        
        self.confidence_label = ttk.Label(conf_frame, text="0%")
        self.confidence_label.pack(side=tk.LEFT)
        
        # Details text
        self.details_text = tk.Text(
            results_frame,
            height=5,
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.details_text.pack(fill=tk.X, pady=5)
        
    def check_backend_status(self):
        """Check if backend services are running."""
        def check():
            statuses = []
            
            # Check NLP backend
            try:
                resp = requests.get(f"{self.backend_url}/health", timeout=2)
                if resp.status_code == 200:
                    statuses.append("✅ NLP Backend")
                else:
                    statuses.append("❌ NLP Backend")
            except:
                statuses.append("❌ NLP Backend")
            
            # Check direct NLP
            if NLP_AVAILABLE:
                statuses.append("✅ Direct NLP")
            else:
                statuses.append("⚠️  Direct NLP")
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(
                text=f"Status: {' | '.join(statuses)}"
            ))
        
        threading.Thread(target=check, daemon=True).start()
    
    def translate(self):
        """Perform translation with NLP enhancement."""
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Empty Input", "Please enter some text to translate.")
            return
        
        # Clear previous results
        self.output_text.delete("1.0", tk.END)
        self.details_text.delete("1.0", tk.END)
        self.translate_btn.config(state="disabled", text="Translating...")
        
        def do_translation():
            try:
                result = None
                
                # Try backend first
                if self.use_nlp_var.get():
                    try:
                        response = requests.post(
                            f"{self.backend_url}/api/nlp/translate",
                            json={
                                "text": input_text,
                                "source": "TCE",
                                "target": "TAU",
                                "use_nlp": True,
                                "include_details": self.show_details_var.get()
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                    except:
                        pass
                
                # Fallback to direct NLP
                if not result and self.nlp_api:
                    result = self.nlp_api.translate(
                        input_text,
                        source="TCE",
                        target="TAU",
                        use_nlp=self.use_nlp_var.get()
                    )
                
                # Update UI with results
                self.root.after(0, lambda: self.display_results(result))
                
            except Exception as e:
                self.root.after(0, lambda: self.display_error(str(e)))
            finally:
                self.root.after(0, lambda: self.translate_btn.config(
                    state="normal", text="Translate →"
                ))
        
        threading.Thread(target=do_translation, daemon=True).start()
    
    def display_results(self, result):
        """Display translation results."""
        if not result:
            self.display_error("No translation result")
            return
        
        # Display translation
        translation = result.get("translation", "")
        self.output_text.insert("1.0", translation)
        
        # Update confidence
        confidence = result.get("confidence", 0.0)
        self.confidence_var.set(confidence * 100)
        self.confidence_label.config(text=f"{confidence*100:.0f}%")
        
        # Show details
        details = []
        
        if "patterns_detected" in result:
            patterns = result["patterns_detected"]
            if patterns:
                details.append(f"Patterns: {', '.join(patterns)}")
        
        if "nlp_enabled" in result:
            details.append(f"NLP: {'Enabled' if result['nlp_enabled'] else 'Disabled'}")
        
        if "execution_time" in result:
            details.append(f"Time: {result['execution_time']*1000:.1f}ms")
        
        if self.show_details_var.get() and "nlp_details" in result:
            details.append("\nNLP Enhancements:")
            for key, value in result["nlp_details"].items():
                if isinstance(value, dict) and not value.get("error"):
                    details.append(f"  - {key}: ✓")
        
        self.details_text.insert("1.0", "\n".join(details))
    
    def display_error(self, error_msg):
        """Display error message."""
        self.output_text.insert("1.0", f"Error: {error_msg}")
        self.confidence_var.set(0)
        self.confidence_label.config(text="0%")
    
    def clear_all(self):
        """Clear all text fields."""
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.details_text.delete("1.0", tk.END)
        self.confidence_var.set(0)
        self.confidence_label.config(text="0%")
    
    def show_examples(self):
        """Show example translations."""
        examples = [
            ("Always x is true", "Basic temporal"),
            ("Sometimes y equals 5", "Sometimes with equality"),
            ("x AND y OR z", "Boolean logic"),
            ("If temperature > 100 then activate cooling", "Conditional"),
            ("The system must always maintain safety", "Requirement"),
        ]
        
        # Create examples window
        examples_win = tk.Toplevel(self.root)
        examples_win.title("Example Translations")
        examples_win.geometry("600x400")
        
        frame = ttk.Frame(examples_win, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="Click an example to use it:",
            font=("Arial", 12)
        ).pack(pady=10)
        
        # Create list
        listbox = tk.Listbox(frame, font=("Consolas", 11), height=10)
        listbox.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for example, description in examples:
            listbox.insert(tk.END, f"{example:<40} # {description}")
        
        def use_example():
            selection = listbox.curselection()
            if selection:
                example_text = examples[selection[0]][0]
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", example_text)
                examples_win.destroy()
        
        ttk.Button(
            frame,
            text="Use Selected",
            command=use_example
        ).pack()


def main():
    """Run the GUI demo."""
    root = tk.Tk()
    
    # Try to use modern theme
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass
    
    app = NLPTranslatorGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    print("🎯 NLP GUI Demo Started")
    print("Try translating: 'Always x is true'")
    
    root.mainloop()


if __name__ == "__main__":
    main()