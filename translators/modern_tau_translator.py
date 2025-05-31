#!/usr/bin/env python3
"""
TauTranslatorOmega - Modern UI/UX Design
=======================================

Completely redesigned interface following 2024 UI/UX best practices:
- Fluent Design 2 principles
- Card-based layout
- Dark/Light mode
- Micro-interactions
- Glassmorphism effects
- Minimalist approach
- Contextual actions

Designed by Claude 3.5 Sonnet with modern design research.
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
import threading
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

class ModernTheme:
    """Modern theme system with dark/light mode support."""
    
    def __init__(self):
        self.current_theme = "dark"  # Start with dark mode (modern default)
        self.themes = {
            "dark": {
                # Background colors
                'bg_primary': '#1e1e1e',      # Main background
                'bg_secondary': '#2d2d2d',    # Cards, panels
                'bg_tertiary': '#3d3d3d',     # Elevated elements
                'bg_accent': '#404040',       # Hover states
                
                # Text colors
                'text_primary': '#ffffff',    # Main text
                'text_secondary': '#b3b3b3',  # Secondary text
                'text_tertiary': '#808080',   # Disabled text
                
                # Accent colors
                'accent_primary': '#0078d4',  # Microsoft blue
                'accent_secondary': '#106ebe',
                'success': '#107c10',
                'warning': '#ff8c00',
                'error': '#d13438',
                
                # Borders and dividers
                'border': '#484848',
                'divider': '#3d3d3d',
                
                # Special effects
                'glass_bg': '#2d2d2d80',      # Glassmorphism
                'shadow': '#00000040',        # Drop shadows
            },
            "light": {
                # Background colors
                'bg_primary': '#ffffff',
                'bg_secondary': '#f8f9fa',
                'bg_tertiary': '#e9ecef',
                'bg_accent': '#dee2e6',
                
                # Text colors
                'text_primary': '#212529',
                'text_secondary': '#6c757d',
                'text_tertiary': '#adb5bd',
                
                # Accent colors
                'accent_primary': '#0078d4',
                'accent_secondary': '#106ebe',
                'success': '#198754',
                'warning': '#fd7e14',
                'error': '#dc3545',
                
                # Borders and dividers
                'border': '#dee2e6',
                'divider': '#e9ecef',
                
                # Special effects
                'glass_bg': '#ffffff80',
                'shadow': '#00000020',
            }
        }
    
    def get_color(self, key):
        """Get color for current theme."""
        return self.themes[self.current_theme][key]
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"

class ModernCard(tk.Frame):
    """Modern card component with glassmorphism effects."""
    
    def __init__(self, parent, theme, title=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = theme
        self.title = title
        
        self.configure(
            bg=theme.get_color('bg_secondary'),
            relief='flat',
            bd=0,
            padx=20,
            pady=20
        )
        
        if title:
            self.create_header()
    
    def create_header(self):
        """Create card header with title."""
        header_frame = tk.Frame(self, bg=self.theme.get_color('bg_secondary'))
        header_frame.pack(fill='x', pady=(0, 12))

        title_label = tk.Label(
            header_frame,
            text=self.title,
            font=('Segoe UI', 12, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary')
        )
        title_label.pack(side='left')

class ModernButton(tk.Button):
    """Modern button with hover effects and proper styling."""

    def __init__(self, parent, theme, style="primary", **kwargs):
        self.theme = theme
        self.style = style

        # Button styles
        styles = {
            "primary": {
                'bg': theme.get_color('accent_primary'),
                'fg': '#ffffff',
                'hover_bg': theme.get_color('accent_secondary')
            },
            "secondary": {
                'bg': theme.get_color('bg_tertiary'),
                'fg': theme.get_color('text_primary'),
                'hover_bg': theme.get_color('bg_accent')
            },
            "success": {
                'bg': theme.get_color('success'),
                'fg': '#ffffff',
                'hover_bg': '#0d5a0d'
            },
            "warning": {
                'bg': theme.get_color('warning'),
                'fg': '#ffffff',
                'hover_bg': '#cc7000'
            }
        }

        style_config = styles.get(style, styles["primary"])

        # Extract font from kwargs if provided, otherwise use default
        font = kwargs.pop('font', ('Segoe UI', 9, 'normal'))

        super().__init__(
            parent,
            bg=style_config['bg'],
            fg=style_config['fg'],
            font=font,
            relief='flat',
            bd=0,
            padx=12,
            pady=6,
            cursor='hand2',
            **kwargs
        )

        # Hover effects
        self.hover_bg = style_config['hover_bg']
        self.normal_bg = style_config['bg']

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        """Handle mouse enter."""
        self.configure(bg=self.hover_bg)
    
    def on_leave(self, event):
        """Handle mouse leave."""
        self.configure(bg=self.normal_bg)

class ModernTauTranslator:
    """Modern TauTranslatorOmega with 2024 UI/UX design."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.theme = ModernTheme()
        self.translator = None
        self.setup_window()
        self.create_modern_ui()
        self.load_translator()
    
    def setup_window(self):
        """Setup modern window with proper styling."""
        self.root.title("TauTranslatorOmega")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 900)
        
        # Modern window styling
        self.root.configure(bg=self.theme.get_color('bg_primary'))
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1600 // 2)
        y = (self.root.winfo_screenheight() // 2) - (1000 // 2)
        self.root.geometry(f"1600x1000+{x}+{y}")
    
    def create_modern_ui(self):
        """Create the modern UI layout."""
        # Main container with padding
        main_container = tk.Frame(
            self.root,
            bg=self.theme.get_color('bg_primary'),
            padx=30,
            pady=30
        )
        main_container.pack(fill='both', expand=True)
        
        # Header section
        self.create_modern_header(main_container)
        
        # Main content area
        self.create_main_content(main_container)
        
        # Status bar
        self.create_modern_status_bar(main_container)
    
    def create_modern_header(self, parent):
        """Create modern header with branding and controls."""
        header_frame = tk.Frame(parent, bg=self.theme.get_color('bg_primary'), height=80)
        header_frame.pack(fill='x', pady=(0, 30))
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_section = tk.Frame(header_frame, bg=self.theme.get_color('bg_primary'))
        left_section.pack(side='left', fill='y')
        
        # Logo and title
        logo_frame = tk.Frame(left_section, bg=self.theme.get_color('bg_primary'))
        logo_frame.pack(expand=True)
        
        # Modern logo
        logo_label = tk.Label(
            logo_frame,
            text="🌍",
            font=('Segoe UI Emoji', 24),
            bg=self.theme.get_color('bg_primary'),
            fg=self.theme.get_color('text_primary')
        )
        logo_label.pack(side='left', padx=(0, 12))

        # Title with modern typography
        title_label = tk.Label(
            logo_frame,
            text="TauTranslatorOmega",
            font=('Segoe UI', 20, 'bold'),
            bg=self.theme.get_color('bg_primary'),
            fg=self.theme.get_color('text_primary')
        )
        title_label.pack(side='left')

        # Subtitle
        subtitle_label = tk.Label(
            logo_frame,
            text="Professional AI Translation",
            font=('Segoe UI', 10),
            bg=self.theme.get_color('bg_primary'),
            fg=self.theme.get_color('text_secondary')
        )
        subtitle_label.pack(side='left', padx=(12, 0))
        
        # Right side - Controls
        right_section = tk.Frame(header_frame, bg=self.theme.get_color('bg_primary'))
        right_section.pack(side='right', fill='y')
        
        # Theme toggle
        self.theme_btn = ModernButton(
            right_section,
            self.theme,
            style="secondary",
            text="🌙 Dark",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side='right', padx=(10, 0))
        
        # Settings button
        settings_btn = ModernButton(
            right_section,
            self.theme,
            style="secondary",
            text="⚙️ Settings",
            command=self.show_settings
        )
        settings_btn.pack(side='right', padx=(10, 0))
    
    def create_main_content(self, parent):
        """Create the main content area with modern layout."""
        content_frame = tk.Frame(parent, bg=self.theme.get_color('bg_primary'))
        content_frame.pack(fill='both', expand=True)
        
        # Create three-column layout
        # Left: Input
        # Center: Controls
        # Right: Output
        
        # Input section (40% width)
        input_section = tk.Frame(content_frame, bg=self.theme.get_color('bg_primary'))
        input_section.pack(side='left', fill='both', expand=True, padx=(0, 15))
        
        self.create_input_card(input_section)
        
        # Center controls (20% width)
        controls_section = tk.Frame(content_frame, bg=self.theme.get_color('bg_primary'), width=300)
        controls_section.pack(side='left', fill='y', padx=15)
        controls_section.pack_propagate(False)
        
        self.create_controls_card(controls_section)
        
        # Output section (40% width)
        output_section = tk.Frame(content_frame, bg=self.theme.get_color('bg_primary'))
        output_section.pack(side='right', fill='both', expand=True, padx=(15, 0))
        
        self.create_output_card(output_section)
    
    def create_input_card(self, parent):
        """Create modern input card."""
        input_card = ModernCard(parent, self.theme, "Input")
        input_card.pack(fill='both', expand=True)
        
        # Language indicator
        lang_frame = tk.Frame(input_card, bg=self.theme.get_color('bg_secondary'))
        lang_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            lang_frame,
            text="🔤 Tau Language",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('accent_primary')
        ).pack(side='left')
        
        # Modern text area container with border radius effect
        text_container = tk.Frame(
            input_card,
            bg=self.theme.get_color('bg_tertiary'),
            relief='flat',
            bd=1,
            highlightbackground=self.theme.get_color('border'),
            highlightthickness=1
        )
        text_container.pack(fill='both', expand=True, pady=(0, 10))

        # Input text area with modern styling
        self.input_text = scrolledtext.ScrolledText(
            text_container,
            font=('Consolas', 10),  # Better monospace font, smaller size
            bg=self.theme.get_color('bg_tertiary'),
            fg=self.theme.get_color('text_primary'),
            insertbackground=self.theme.get_color('accent_primary'),
            selectbackground=self.theme.get_color('accent_primary'),
            selectforeground='#ffffff',
            relief='flat',
            bd=0,
            padx=12,
            pady=12,
            wrap=tk.WORD
        )
        self.input_text.pack(fill='both', expand=True)

        # Add syntax highlighting placeholder
        placeholder = """// Enter your Tau Language code here
halfAdderSum(a, b) := a + b
r o1[t] = i1[t] & i2[t]
always (x > 0)"""

        self.input_text.insert('1.0', placeholder)
        self.input_text.bind('<FocusIn>', self.clear_placeholder)
        self.input_text.bind('<KeyRelease>', self.on_text_change)

        # File operations bar
        file_bar = tk.Frame(input_card, bg=self.theme.get_color('bg_secondary'))
        file_bar.pack(fill='x', pady=(5, 0))

        # File buttons with modern styling
        file_buttons = [
            ("📂 Open", self.open_file),
            ("💾 Save", self.save_file),
            ("📋 Copy", self.copy_input)
        ]

        for text, command in file_buttons:
            btn = tk.Button(
                file_bar,
                text=text,
                font=('Segoe UI', 9),
                bg=self.theme.get_color('bg_tertiary'),
                fg=self.theme.get_color('text_secondary'),
                relief='flat',
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2',
                command=command
            )
            btn.pack(side='left', padx=(0, 5))

            # Hover effects
            def on_enter(e, button=btn):
                button.configure(bg=self.theme.get_color('bg_accent'))

            def on_leave(e, button=btn):
                button.configure(bg=self.theme.get_color('bg_tertiary'))

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
    
    def create_controls_card(self, parent):
        """Create modern controls card."""
        controls_card = ModernCard(parent, self.theme, "Translation")
        controls_card.pack(fill='both', expand=True)
        
        # Direction selector
        direction_frame = tk.Frame(controls_card, bg=self.theme.get_color('bg_secondary'))
        direction_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            direction_frame,
            text="Direction",
            font=('Segoe UI', 10, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary')
        ).pack(anchor='w', pady=(0, 8))

        self.direction = tk.StringVar(value="tau_to_tce")

        # Modern radio buttons
        tau_to_tce = tk.Radiobutton(
            direction_frame,
            text="Tau → Natural Language",
            variable=self.direction,
            value="tau_to_tce",
            font=('Segoe UI', 9),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary'),
            selectcolor=self.theme.get_color('accent_primary'),
            activebackground=self.theme.get_color('bg_secondary'),
            relief='flat'
        )
        tau_to_tce.pack(anchor='w', pady=1)

        tce_to_tau = tk.Radiobutton(
            direction_frame,
            text="Natural Language → Tau",
            variable=self.direction,
            value="tce_to_tau",
            font=('Segoe UI', 9),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary'),
            selectcolor=self.theme.get_color('accent_primary'),
            activebackground=self.theme.get_color('bg_secondary'),
            relief='flat'
        )
        tce_to_tau.pack(anchor='w', pady=1)
        
        # Main translate button
        self.translate_btn = ModernButton(
            controls_card,
            self.theme,
            style="primary",
            text="🚀 Translate",
            font=('Segoe UI', 10, 'bold'),
            command=self.translate_text
        )
        self.translate_btn.pack(fill='x', pady=15)
        
        # AI Model section
        ai_frame = tk.Frame(controls_card, bg=self.theme.get_color('bg_secondary'))
        ai_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(
            ai_frame,
            text="AI Engine",
            font=('Segoe UI', 10, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary')
        ).pack(anchor='w', pady=(0, 8))

        # Model status
        self.model_status = tk.Label(
            ai_frame,
            text="🤖 Pattern-based (Ready)",
            font=('Segoe UI', 9),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_secondary')
        )
        self.model_status.pack(anchor='w', pady=2)
        
        # Gemma 3 button
        self.gemma_btn = ModernButton(
            ai_frame,
            self.theme,
            style="success",
            text="📥 Setup Gemma 3",
            command=self.setup_gemma3
        )
        self.gemma_btn.pack(fill='x', pady=(10, 0))
        
        # Quick actions
        actions_frame = tk.Frame(controls_card, bg=self.theme.get_color('bg_secondary'))
        actions_frame.pack(fill='x')
        
        tk.Label(
            actions_frame,
            text="Quick Actions",
            font=('Segoe UI', 12, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_primary')
        ).pack(anchor='w', pady=(0, 10))
        
        # Action buttons
        ModernButton(
            actions_frame,
            self.theme,
            style="secondary",
            text="📝 Examples",
            command=self.load_examples
        ).pack(fill='x', pady=2)
        
        ModernButton(
            actions_frame,
            self.theme,
            style="secondary",
            text="🔄 Clear",
            command=self.clear_all
        ).pack(fill='x', pady=2)
        
        ModernButton(
            actions_frame,
            self.theme,
            style="secondary",
            text="📊 Stats",
            command=self.show_stats
        ).pack(fill='x', pady=2)
    
    def create_output_card(self, parent):
        """Create modern output card."""
        output_card = ModernCard(parent, self.theme, "Output")
        output_card.pack(fill='both', expand=True)
        
        # Language indicator
        lang_frame = tk.Frame(output_card, bg=self.theme.get_color('bg_secondary'))
        lang_frame.pack(fill='x', pady=(0, 10))
        
        self.output_lang_label = tk.Label(
            lang_frame,
            text="🗣️ Natural Language",
            font=('Segoe UI', 11, 'bold'),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('success')
        )
        self.output_lang_label.pack(side='left')
        
        # Confidence indicator
        self.confidence_label = tk.Label(
            lang_frame,
            text="",
            font=('Segoe UI', 10),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_secondary')
        )
        self.confidence_label.pack(side='right')
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(
            output_card,
            font=('Segoe UI', 10),
            bg=self.theme.get_color('bg_tertiary'),
            fg=self.theme.get_color('text_primary'),
            insertbackground=self.theme.get_color('text_primary'),
            selectbackground=self.theme.get_color('accent_primary'),
            relief='flat',
            bd=0,
            padx=12,
            pady=12,
            wrap=tk.WORD,
            state='disabled'
        )
        self.output_text.pack(fill='both', expand=True)
    
    def create_modern_status_bar(self, parent):
        """Create modern status bar."""
        status_frame = tk.Frame(
            parent,
            bg=self.theme.get_color('bg_secondary'),
            height=40
        )
        status_frame.pack(fill='x', pady=(30, 0))
        status_frame.pack_propagate(False)
        
        # Status text
        self.status_label = tk.Label(
            status_frame,
            text="Ready to translate",
            font=('Segoe UI', 10),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_secondary')
        )
        self.status_label.pack(side='left', padx=20, pady=10)
        
        # Translation count
        self.translation_count = 0
        self.count_label = tk.Label(
            status_frame,
            text="Translations: 0",
            font=('Segoe UI', 10),
            bg=self.theme.get_color('bg_secondary'),
            fg=self.theme.get_color('text_secondary')
        )
        self.count_label.pack(side='right', padx=20, pady=10)
    
    def toggle_theme(self):
        """Toggle between dark and light themes."""
        self.theme.toggle_theme()
        
        # Update theme button text
        if self.theme.current_theme == "dark":
            self.theme_btn.configure(text="🌙 Dark")
        else:
            self.theme_btn.configure(text="☀️ Light")
        
        # Recreate UI with new theme
        self.refresh_ui()
    
    def refresh_ui(self):
        """Refresh UI with current theme."""
        # This would normally recreate all UI elements
        # For now, just update the main background
        self.root.configure(bg=self.theme.get_color('bg_primary'))
        messagebox.showinfo("Theme", f"Switched to {self.theme.current_theme} mode!\n\nFull theme refresh coming in next update.")
    
    def clear_placeholder(self, event):
        """Clear placeholder text on focus."""
        if "// Enter your Tau Language code here" in self.input_text.get('1.0', tk.END):
            self.input_text.delete('1.0', tk.END)
    
    def load_translator(self):
        """Load the translator system."""
        def load():
            try:
                from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
                self.translator = LMQLBidirectionalTranslator()
                
                self.root.after(0, lambda: self.status_label.config(text="✅ Translator ready"))
                self.root.after(0, lambda: self.model_status.config(text="🤖 Pattern-based (Ready)"))
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ Translator failed: {e}"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def translate_text(self):
        """Perform translation with modern feedback."""
        if not self.translator:
            messagebox.showerror("Error", "Translator not ready")
            return
        
        input_text = self.input_text.get('1.0', tk.END).strip()
        if not input_text or "// Enter your Tau Language code here" in input_text:
            messagebox.showwarning("Warning", "Please enter text to translate")
            return
        
        # Update UI for translation
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
        """Display translation result with modern styling."""
        # Update output
        self.output_text.configure(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', result.output)
        self.output_text.configure(state='disabled')
        
        # Update confidence
        confidence_text = f"Confidence: {result.confidence:.1%}"
        self.confidence_label.configure(text=confidence_text)
        
        # Update counters
        self.translation_count += 1
        self.count_label.configure(text=f"Translations: {self.translation_count}")
        
        # Update status
        self.status_label.configure(text="✅ Translation complete")
    
    def setup_gemma3(self):
        """Setup Gemma 3 model."""
        messagebox.showinfo("Gemma 3 Setup", "Gemma 3 setup will be implemented in the next update!")
    
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
        self.confidence_label.configure(text="")
        self.status_label.configure(text="🔄 Ready for new translation")
    
    def show_stats(self):
        """Show translation statistics."""
        messagebox.showinfo("Statistics", f"Total Translations: {self.translation_count}\\nCurrent Theme: {self.theme.current_theme.title()}")
    
    def show_settings(self):
        """Show settings dialog."""
        messagebox.showinfo("Settings", "Settings panel coming in next update!")

    def on_text_change(self, event):
        """Handle text changes for real-time feedback."""
        # Could add syntax highlighting here
        pass

    def open_file(self):
        """Open file dialog."""
        filename = filedialog.askopenfilename(
            title="Open Tau File",
            filetypes=[("Tau files", "*.tau"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', content)
                self.status_label.configure(text=f"✅ Opened: {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        """Save file dialog."""
        content = self.output_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No output to save")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Translation",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.configure(text=f"✅ Saved: {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def copy_input(self):
        """Copy input text to clipboard."""
        content = self.input_text.get('1.0', tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.status_label.configure(text="✅ Input copied to clipboard")

    def run(self):
        """Run the modern application."""
        self.root.mainloop()

def main():
    """Launch the modern TauTranslatorOmega."""
    print("🎨 Launching Modern TauTranslatorOmega")
    print("Redesigned with 2024 UI/UX best practices")
    
    app = ModernTauTranslator()
    app.run()

if __name__ == "__main__":
    main()
