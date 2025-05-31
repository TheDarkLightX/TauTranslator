#!/usr/bin/env python3
"""
TauTranslatorOmega - Improved Modern UI
======================================

Properly working dark/light mode toggle and refined UI/UX.
Fixed all the issues from the previous version.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class ImprovedTheme:
    """Improved theme system with working dark/light mode."""
    
    def __init__(self):
        self.current_theme = "dark"
        self.themes = {
            "dark": {
                'bg_primary': '#1e1e1e',
                'bg_secondary': '#2d2d2d',
                'bg_tertiary': '#3a3a3a',
                'text_primary': '#ffffff',
                'text_secondary': '#cccccc',
                'text_tertiary': '#999999',
                'accent': '#0078d4',
                'accent_hover': '#106ebe',
                'success': '#16a085',
                'warning': '#f39c12',
                'error': '#e74c3c',
                'border': '#555555',
            },
            "light": {
                'bg_primary': '#ffffff',
                'bg_secondary': '#f8f9fa',
                'bg_tertiary': '#e9ecef',
                'text_primary': '#212529',
                'text_secondary': '#495057',
                'text_tertiary': '#6c757d',
                'accent': '#0078d4',
                'accent_hover': '#106ebe',
                'success': '#28a745',
                'warning': '#ffc107',
                'error': '#dc3545',
                'border': '#dee2e6',
            }
        }
    
    def get(self, key):
        """Get color for current theme."""
        return self.themes[self.current_theme][key]
    
    def toggle(self):
        """Toggle between themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"

class ModernWidget:
    """Base class for modern widgets with theme support."""
    
    def __init__(self, theme):
        self.theme = theme
    
    def apply_theme(self, widget, bg_key='bg_secondary', fg_key='text_primary'):
        """Apply theme colors to a widget."""
        try:
            widget.configure(
                bg=self.theme.get(bg_key),
                fg=self.theme.get(fg_key)
            )
        except tk.TclError:
            pass  # Some widgets don't support all options

class ImprovedTauTranslator:
    """Improved TauTranslator with working theme system."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.theme = ImprovedTheme()
        self.translator = None
        self.widgets = []  # Track widgets for theme updates
        
        self.setup_window()
        self.create_ui()
        self.load_translator()
    
    def setup_window(self):
        """Setup the main window."""
        self.root.title("TauTranslatorOmega - Improved")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Apply initial theme
        self.root.configure(bg=self.theme.get('bg_primary'))
    
    def create_ui(self):
        """Create the improved UI."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg=self.theme.get('bg_primary'))
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Content area
        self.create_content()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Create improved header."""
        header_frame = tk.Frame(self.main_frame, bg=self.theme.get('bg_secondary'), height=70)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Left side - Title
        left_frame = tk.Frame(header_frame, bg=self.theme.get('bg_secondary'))
        left_frame.pack(side='left', fill='y', padx=20)
        
        title_frame = tk.Frame(left_frame, bg=self.theme.get('bg_secondary'))
        title_frame.pack(expand=True)
        
        # Logo and title
        self.title_label = tk.Label(
            title_frame,
            text="🌍 TauTranslatorOmega",
            font=('Segoe UI', 18, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.title_label.pack(side='left')
        
        self.subtitle_label = tk.Label(
            title_frame,
            text="Professional Translation",
            font=('Segoe UI', 10),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_secondary')
        )
        self.subtitle_label.pack(side='left', padx=(15, 0))
        
        # Right side - Controls
        right_frame = tk.Frame(header_frame, bg=self.theme.get('bg_secondary'))
        right_frame.pack(side='right', fill='y', padx=20)
        
        controls_frame = tk.Frame(right_frame, bg=self.theme.get('bg_secondary'))
        controls_frame.pack(expand=True)
        
        # Theme toggle button
        self.theme_btn = tk.Button(
            controls_frame,
            text="☀️ Light Mode",
            font=('Segoe UI', 9),
            bg=self.theme.get('accent'),
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.toggle_theme
        )
        self.theme_btn.pack(side='right', padx=(10, 0))
        
        # Add widgets to tracking list
        self.widgets.extend([
            (header_frame, 'bg_secondary', 'text_primary'),
            (left_frame, 'bg_secondary', 'text_primary'),
            (title_frame, 'bg_secondary', 'text_primary'),
            (self.title_label, 'bg_secondary', 'text_primary'),
            (self.subtitle_label, 'bg_secondary', 'text_secondary'),
            (right_frame, 'bg_secondary', 'text_primary'),
            (controls_frame, 'bg_secondary', 'text_primary')
        ])
    
    def create_content(self):
        """Create main content area."""
        content_frame = tk.Frame(self.main_frame, bg=self.theme.get('bg_primary'))
        content_frame.pack(fill='both', expand=True)
        
        # Three sections: Input, Controls, Output
        self.create_input_section(content_frame)
        self.create_controls_section(content_frame)
        self.create_output_section(content_frame)
    
    def create_input_section(self, parent):
        """Create input section."""
        input_frame = tk.Frame(parent, bg=self.theme.get('bg_secondary'))
        input_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Header
        input_header = tk.Frame(input_frame, bg=self.theme.get('bg_secondary'), height=40)
        input_header.pack(fill='x', padx=15, pady=10)
        input_header.pack_propagate(False)
        
        self.input_title = tk.Label(
            input_header,
            text="📝 Input (Tau Language)",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.input_title.pack(side='left', expand=True)
        
        # Text area
        self.input_text = scrolledtext.ScrolledText(
            input_frame,
            font=('Consolas', 10),
            bg=self.theme.get('bg_tertiary'),
            fg=self.theme.get('text_primary'),
            insertbackground=self.theme.get('accent'),
            selectbackground=self.theme.get('accent'),
            relief='flat',
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD
        )
        self.input_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Add example text
        example = """// Example Tau Language Code
halfAdderSum(a, b) := a + b
r o1[t] = i1[t] & i2[t]
always (x > 0)"""
        self.input_text.insert('1.0', example)
        
        # Add to widgets list
        self.widgets.extend([
            (input_frame, 'bg_secondary', 'text_primary'),
            (input_header, 'bg_secondary', 'text_primary'),
            (self.input_title, 'bg_secondary', 'text_primary'),
            (self.input_text, 'bg_tertiary', 'text_primary')
        ])
    
    def create_controls_section(self, parent):
        """Create controls section."""
        controls_frame = tk.Frame(parent, bg=self.theme.get('bg_secondary'), width=250)
        controls_frame.pack(side='left', fill='y', padx=10)
        controls_frame.pack_propagate(False)
        
        # Header
        controls_header = tk.Frame(controls_frame, bg=self.theme.get('bg_secondary'), height=40)
        controls_header.pack(fill='x', padx=15, pady=10)
        controls_header.pack_propagate(False)
        
        self.controls_title = tk.Label(
            controls_header,
            text="🔄 Translation Controls",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.controls_title.pack(expand=True)
        
        # Direction selection
        direction_frame = tk.Frame(controls_frame, bg=self.theme.get('bg_secondary'))
        direction_frame.pack(fill='x', padx=15, pady=10)
        
        self.direction_label = tk.Label(
            direction_frame,
            text="Direction:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.direction_label.pack(anchor='w', pady=(0, 5))
        
        self.direction = tk.StringVar(value="tau_to_tce")
        
        self.radio1 = tk.Radiobutton(
            direction_frame,
            text="Tau → Natural Language",
            variable=self.direction,
            value="tau_to_tce",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary'),
            selectcolor=self.theme.get('accent'),
            relief='flat'
        )
        self.radio1.pack(anchor='w', pady=2)
        
        self.radio2 = tk.Radiobutton(
            direction_frame,
            text="Natural Language → Tau",
            variable=self.direction,
            value="tce_to_tau",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary'),
            selectcolor=self.theme.get('accent'),
            relief='flat'
        )
        self.radio2.pack(anchor='w', pady=2)
        
        # Translate button
        self.translate_btn = tk.Button(
            controls_frame,
            text="🚀 Translate",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get('accent'),
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            cursor='hand2',
            command=self.translate_text
        )
        self.translate_btn.pack(fill='x', padx=15, pady=20)
        
        # Model status
        model_frame = tk.Frame(controls_frame, bg=self.theme.get('bg_secondary'))
        model_frame.pack(fill='x', padx=15, pady=10)
        
        self.model_label = tk.Label(
            model_frame,
            text="AI Model:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.model_label.pack(anchor='w', pady=(0, 5))
        
        self.model_status = tk.Label(
            model_frame,
            text="🤖 Pattern-based (Ready)",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_secondary')
        )
        self.model_status.pack(anchor='w')
        
        # Quick actions
        actions_frame = tk.Frame(controls_frame, bg=self.theme.get('bg_secondary'))
        actions_frame.pack(fill='x', padx=15, pady=10)
        
        self.actions_label = tk.Label(
            actions_frame,
            text="Quick Actions:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.actions_label.pack(anchor='w', pady=(0, 5))
        
        # Action buttons
        self.examples_btn = tk.Button(
            actions_frame,
            text="📝 Load Examples",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_tertiary'),
            fg=self.theme.get('text_primary'),
            relief='flat',
            padx=10,
            pady=6,
            cursor='hand2',
            command=self.load_examples
        )
        self.examples_btn.pack(fill='x', pady=2)
        
        self.clear_btn = tk.Button(
            actions_frame,
            text="🔄 Clear All",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_tertiary'),
            fg=self.theme.get('text_primary'),
            relief='flat',
            padx=10,
            pady=6,
            cursor='hand2',
            command=self.clear_all
        )
        self.clear_btn.pack(fill='x', pady=2)
        
        # Add to widgets list
        self.widgets.extend([
            (controls_frame, 'bg_secondary', 'text_primary'),
            (controls_header, 'bg_secondary', 'text_primary'),
            (self.controls_title, 'bg_secondary', 'text_primary'),
            (direction_frame, 'bg_secondary', 'text_primary'),
            (self.direction_label, 'bg_secondary', 'text_primary'),
            (self.radio1, 'bg_secondary', 'text_primary'),
            (self.radio2, 'bg_secondary', 'text_primary'),
            (model_frame, 'bg_secondary', 'text_primary'),
            (self.model_label, 'bg_secondary', 'text_primary'),
            (self.model_status, 'bg_secondary', 'text_secondary'),
            (actions_frame, 'bg_secondary', 'text_primary'),
            (self.actions_label, 'bg_secondary', 'text_primary'),
            (self.examples_btn, 'bg_tertiary', 'text_primary'),
            (self.clear_btn, 'bg_tertiary', 'text_primary')
        ])
    
    def create_output_section(self, parent):
        """Create output section."""
        output_frame = tk.Frame(parent, bg=self.theme.get('bg_secondary'))
        output_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # Header
        output_header = tk.Frame(output_frame, bg=self.theme.get('bg_secondary'), height=40)
        output_header.pack(fill='x', padx=15, pady=10)
        output_header.pack_propagate(False)
        
        self.output_title = tk.Label(
            output_header,
            text="🗣️ Output (Natural Language)",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_primary')
        )
        self.output_title.pack(side='left', expand=True)
        
        # Text area
        self.output_text = scrolledtext.ScrolledText(
            output_frame,
            font=('Segoe UI', 10),
            bg=self.theme.get('bg_tertiary'),
            fg=self.theme.get('text_primary'),
            insertbackground=self.theme.get('accent'),
            selectbackground=self.theme.get('accent'),
            relief='flat',
            bd=0,
            padx=15,
            pady=15,
            wrap=tk.WORD,
            state='disabled'
        )
        self.output_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Add to widgets list
        self.widgets.extend([
            (output_frame, 'bg_secondary', 'text_primary'),
            (output_header, 'bg_secondary', 'text_primary'),
            (self.output_title, 'bg_secondary', 'text_primary'),
            (self.output_text, 'bg_tertiary', 'text_primary')
        ])
    
    def create_status_bar(self):
        """Create status bar."""
        status_frame = tk.Frame(self.main_frame, bg=self.theme.get('bg_secondary'), height=35)
        status_frame.pack(fill='x', pady=(20, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready to translate",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_secondary')
        )
        self.status_label.pack(side='left', padx=15, pady=8)
        
        self.translation_count = 0
        self.count_label = tk.Label(
            status_frame,
            text="Translations: 0",
            font=('Segoe UI', 9),
            bg=self.theme.get('bg_secondary'),
            fg=self.theme.get('text_secondary')
        )
        self.count_label.pack(side='right', padx=15, pady=8)
        
        # Add to widgets list
        self.widgets.extend([
            (status_frame, 'bg_secondary', 'text_primary'),
            (self.status_label, 'bg_secondary', 'text_secondary'),
            (self.count_label, 'bg_secondary', 'text_secondary')
        ])
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.theme.toggle()
        
        # Update theme button text
        if self.theme.current_theme == "dark":
            self.theme_btn.configure(text="☀️ Light Mode")
        else:
            self.theme_btn.configure(text="🌙 Dark Mode")
        
        # Update all widgets
        self.apply_theme_to_all_widgets()
    
    def apply_theme_to_all_widgets(self):
        """Apply current theme to all tracked widgets."""
        # Update root
        self.root.configure(bg=self.theme.get('bg_primary'))
        self.main_frame.configure(bg=self.theme.get('bg_primary'))
        
        # Update theme button
        self.theme_btn.configure(bg=self.theme.get('accent'))
        self.translate_btn.configure(bg=self.theme.get('accent'))
        
        # Update all tracked widgets
        for widget, bg_key, fg_key in self.widgets:
            try:
                widget.configure(
                    bg=self.theme.get(bg_key),
                    fg=self.theme.get(fg_key)
                )
            except tk.TclError:
                pass  # Some widgets don't support all options
    
    def load_translator(self):
        """Load the translator system."""
        def load():
            try:
                from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
                self.translator = LMQLBidirectionalTranslator()
                
                self.root.after(0, lambda: self.status_label.config(text="✅ Translator ready"))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ Translator failed: {e}"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def translate_text(self):
        """Perform translation."""
        if not self.translator:
            messagebox.showerror("Error", "Translator not ready")
            return
        
        input_text = self.input_text.get('1.0', tk.END).strip()
        if not input_text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        # Update UI
        self.translate_btn.configure(text="🔄 Translating...", state='disabled')
        self.status_label.configure(text="🔄 Translating...")
        
        def translate():
            try:
                direction = self.direction.get()
                
                if direction == "tau_to_tce":
                    result = self.translator.translate_tau_to_tce(input_text)
                else:
                    result = self.translator.translate_tce_to_tau(input_text)
                
                if result.success:
                    self.root.after(0, lambda: self.display_result(result))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Translation Failed", "\\n".join(result.errors)))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Translation error: {e}"))
            finally:
                self.root.after(0, lambda: self.translate_btn.configure(text="🚀 Translate", state='normal'))
        
        threading.Thread(target=translate, daemon=True).start()
    
    def display_result(self, result):
        """Display translation result."""
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', result.output)
        self.output_text.configure(state='disabled')
        
        self.translation_count += 1
        self.count_label.configure(text=f"Translations: {self.translation_count}")
        self.status_label.configure(text="✅ Translation complete")
    
    def load_examples(self):
        """Load example code."""
        examples = """// 4-bit Binary Adder
halfAdderSum(a, b) := a + b
halfAdderCarry(a, b) := a & b

// Logic Gates
r and_gate[t] = i1[t] & i2[t]
r or_gate[t] = i1[t] | i2[t]

// Temporal Logic
always (x > 0)
sometimes (status = ready)"""
        
        self.input_text.delete('1.0', tk.END)
        self.input_text.insert('1.0', examples)
        self.status_label.configure(text="✅ Examples loaded")
    
    def clear_all(self):
        """Clear all text areas."""
        self.input_text.delete('1.0', tk.END)
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.configure(state='disabled')
        self.status_label.configure(text="🔄 Ready for new translation")
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Launch the improved application."""
    print("🎨 Launching Improved TauTranslatorOmega")
    print("With working dark/light mode and refined UI")
    
    app = ImprovedTauTranslator()
    app.run()

if __name__ == "__main__":
    main()
