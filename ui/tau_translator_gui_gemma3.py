#!/usr/bin/env python3
"""
TauTranslatorOmega GUI with Gemma 3
===================================

Desktop GUI application with Google's Gemma 3 model integration.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class TauTranslatorGemma3GUI:
    """Main GUI application with Gemma 3 support."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("TauTranslatorOmega - Gemma 3 Enhanced")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        # Initialize components
        self.translator = None
        self.gemma3_available = False
        self.gemma3_loaded = False
        
        self.setup_gui()
        self.load_translator()
    
    def setup_gui(self):
        """Set up the GUI components."""
        # Title section
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        title_frame.pack(fill="x", padx=10, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🤖 TauTranslatorOmega",
            font=("Arial", 28, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Enhanced with Google Gemma 3 • Bidirectional Tau ↔ TCE Translation",
            font=("Arial", 12),
            fg="#ecf0f1",
            bg="#2c3e50"
        )
        subtitle_label.pack()
        
        # Status section
        status_frame = tk.Frame(self.root, bg="#27ae60", height=50)
        status_frame.pack(fill="x", padx=10, pady=2)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="🔧 Loading translator...",
            font=("Arial", 11, "bold"),
            fg="white",
            bg="#27ae60"
        )
        self.status_label.pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Translation area
        translation_frame = tk.Frame(main_frame, bg="#f0f0f0")
        translation_frame.pack(fill="both", expand=True)
        
        # Input section
        input_frame = tk.LabelFrame(
            translation_frame,
            text="📝 Input (Tau Language)",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        input_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            height=20,
            font=("Courier New", 11),
            wrap=tk.WORD
        )
        self.input_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insert example
        example_tau = """halfAdderSum(a, b) := a + b
r o1[t] = i1[t] & i2[t]
always (x > 0)
sbf i1 = ifile("data.in")"""
        self.input_text.insert("1.0", example_tau)
        
        # Control section
        control_frame = tk.Frame(translation_frame, bg="#f0f0f0", width=200)
        control_frame.pack(side="left", fill="y", padx=10)
        control_frame.pack_propagate(False)
        
        # Direction selection
        direction_label = tk.Label(
            control_frame,
            text="Translation Direction:",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0"
        )
        direction_label.pack(pady=10)
        
        self.direction = tk.StringVar(value="tau_to_tce")
        
        tau_to_tce_btn = tk.Radiobutton(
            control_frame,
            text="Tau → TCE",
            variable=self.direction,
            value="tau_to_tce",
            font=("Arial", 10),
            bg="#f0f0f0",
            command=self.update_labels
        )
        tau_to_tce_btn.pack(pady=5)
        
        tce_to_tau_btn = tk.Radiobutton(
            control_frame,
            text="TCE → Tau",
            variable=self.direction,
            value="tce_to_tau",
            font=("Arial", 10),
            bg="#f0f0f0",
            command=self.update_labels
        )
        tce_to_tau_btn.pack(pady=5)
        
        # Translate button
        translate_btn = tk.Button(
            control_frame,
            text="🚀 Translate",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            command=self.translate_text,
            width=15,
            height=2
        )
        translate_btn.pack(pady=20)
        
        # Model status
        model_frame = tk.LabelFrame(
            control_frame,
            text="Model Status",
            font=("Arial", 10, "bold"),
            bg="#f0f0f0"
        )
        model_frame.pack(fill="x", pady=10)
        
        self.model_status = tk.Label(
            model_frame,
            text="🔧 Loading...",
            font=("Arial", 9),
            bg="#f0f0f0",
            wraplength=150,
            justify="left"
        )
        self.model_status.pack(padx=5, pady=5)
        
        # Load Gemma 3 button
        load_gemma3_btn = tk.Button(
            control_frame,
            text="📥 Load Gemma 3",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self.load_gemma3,
            width=15
        )
        load_gemma3_btn.pack(pady=5)
        
        # Setup Gemma 3 button
        setup_gemma3_btn = tk.Button(
            control_frame,
            text="⚙️ Setup Gemma 3",
            font=("Arial", 10),
            bg="#9b59b6",
            fg="white",
            command=self.setup_gemma3,
            width=15
        )
        setup_gemma3_btn.pack(pady=5)
        
        # Output section
        output_frame = tk.LabelFrame(
            translation_frame,
            text="🗣️ Output (TCE)",
            font=("Arial", 12, "bold"),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        output_frame.pack(side="right", fill="both", expand=True, padx=5)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            height=20,
            font=("Courier New", 11),
            wrap=tk.WORD,
            state="disabled"
        )
        self.output_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Info section
        info_frame = tk.Frame(main_frame, bg="#ecf0f1", height=120)
        info_frame.pack(fill="x", pady=5)
        info_frame.pack_propagate(False)
        
        info_label = tk.Label(
            info_frame,
            text="ℹ️ Translation Info",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1"
        )
        info_label.pack(anchor="w", padx=10, pady=5)
        
        self.info_text = tk.Text(
            info_frame,
            height=6,
            font=("Arial", 9),
            bg="#ecf0f1",
            state="disabled",
            wrap=tk.WORD
        )
        self.info_text.pack(fill="both", expand=True, padx=10, pady=5)
    
    def load_translator(self):
        """Load the translator in background."""
        def load():
            try:
                from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
                self.translator = LMQLBidirectionalTranslator()
                
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ Pattern-based translator ready",
                    bg="#27ae60"
                ))
                
                self.root.after(0, lambda: self.model_status.config(
                    text="📝 Pattern-based\\nready\\n\\n🤖 Gemma 3\\nnot loaded"
                ))
                
                # Check if Gemma 3 is available
                try:
                    from tau_translator_omega.gemma3.translator import gemma3_translator
                    self.gemma3_available = True
                    self.root.after(0, lambda: self.model_status.config(
                        text="📝 Pattern-based\\nready\\n\\n🤖 Gemma 3\\navailable"
                    ))
                except ImportError:
                    pass
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"❌ Translator failed: {e}",
                    bg="#e74c3c"
                ))
        
        threading.Thread(target=load, daemon=True).start()
    
    def load_gemma3(self):
        """Load Gemma 3 model."""
        if not self.gemma3_available:
            messagebox.showwarning("Gemma 3 Not Available", 
                                 "Gemma 3 is not set up. Click 'Setup Gemma 3' first.")
            return
        
        def load():
            try:
                from tau_translator_omega.gemma3.translator import gemma3_translator
                
                self.root.after(0, lambda: self.model_status.config(
                    text="🔄 Loading\\nGemma 3..."
                ))
                
                success = gemma3_translator.load_model()
                
                if success:
                    self.gemma3_loaded = True
                    self.root.after(0, lambda: self.model_status.config(
                        text="📝 Pattern-based\\nready\\n\\n🤖 Gemma 3\\nLOADED"
                    ))
                    self.root.after(0, lambda: self.status_label.config(
                        text="🚀 Enhanced translation with Gemma 3",
                        bg="#27ae60"
                    ))
                else:
                    self.root.after(0, lambda: self.model_status.config(
                        text="📝 Pattern-based\\nready\\n\\n❌ Gemma 3\\nfailed"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Gemma 3 Error", f"Failed to load Gemma 3: {e}"
                ))
        
        threading.Thread(target=load, daemon=True).start()
    
    def setup_gemma3(self):
        """Setup Gemma 3 model."""
        result = messagebox.askyesno(
            "Setup Gemma 3",
            "This will download Google's Gemma 3 model (~5GB).\\n\\n"
            "This may take several minutes and requires internet.\\n\\n"
            "Continue?"
        )
        
        if result:
            def setup():
                try:
                    import subprocess
                    
                    self.root.after(0, lambda: self.status_label.config(
                        text="📥 Setting up Gemma 3... (this may take several minutes)",
                        bg="#f39c12"
                    ))
                    
                    # Run the setup script
                    result = subprocess.run([
                        sys.executable, "setup_gemma3.py"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.gemma3_available = True
                        self.root.after(0, lambda: self.status_label.config(
                            text="✅ Gemma 3 setup complete! Click 'Load Gemma 3'",
                            bg="#27ae60"
                        ))
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Setup Complete",
                            "Gemma 3 has been set up successfully!\\n\\n"
                            "Click 'Load Gemma 3' to start using it."
                        ))
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text="❌ Gemma 3 setup failed",
                            bg="#e74c3c"
                        ))
                        self.root.after(0, lambda: messagebox.showerror(
                            "Setup Failed",
                            f"Gemma 3 setup failed:\\n{result.stderr}"
                        ))
                        
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Setup Error", f"Setup error: {e}"
                    ))
            
            threading.Thread(target=setup, daemon=True).start()
    
    def update_labels(self):
        """Update labels based on direction."""
        # This would update the frame labels
        pass
    
    def translate_text(self):
        """Translate the input text."""
        if not self.translator:
            messagebox.showerror("Error", "Translator not loaded")
            return
        
        input_text = self.input_text.get("1.0", tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        def translate():
            try:
                direction = self.direction.get()
                
                # Perform translation
                if direction == "tau_to_tce":
                    result = self.translator.translate_tau_to_tce(input_text)
                else:
                    result = self.translator.translate_tce_to_tau(input_text)
                
                if result.success:
                    method = "🤖 Gemma 3" if self.gemma3_loaded else "📝 Pattern-based"
                    self.root.after(0, lambda: self.display_result(
                        result.output, method, result.confidence, result.patterns_detected
                    ))
                else:
                    self.root.after(0, lambda: messagebox.showerror(
                        "Translation Failed", 
                        "\\n".join(result.errors)
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", 
                    f"Translation error: {e}"
                ))
        
        # Show loading
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", "🔄 Translating...")
        self.output_text.config(state="disabled")
        
        threading.Thread(target=translate, daemon=True).start()
    
    def display_result(self, result_text, method, confidence, patterns):
        """Display translation result."""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", result_text)
        self.output_text.config(state="disabled")
        
        # Update info
        info_text = f"""Translation completed successfully!

Method: {method}
Confidence: {confidence:.1%}
Patterns detected: {', '.join(patterns)}

Quality: {'High (AI-enhanced)' if 'Gemma' in method else 'Good (Pattern-based)'}
"""
        
        self.info_text.config(state="normal")
        self.info_text.delete("1.0", tk.END)
        self.info_text.insert("1.0", info_text)
        self.info_text.config(state="disabled")
        
        # Update status
        self.status_label.config(
            text=f"✅ Translation complete - {method} ({confidence:.1%} confidence)"
        )
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

def main():
    """Run the Gemma 3 enhanced GUI."""
    print("🚀 Starting TauTranslatorOmega with Gemma 3 support")
    
    app = TauTranslatorGemma3GUI()
    app.run()

if __name__ == "__main__":
    main()
