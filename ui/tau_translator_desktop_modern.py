#!/usr/bin/env python3
"""
TauTranslatorOmega - Modern Professional GUI
===========================================

A modern, professional desktop interface that matches and exceeds
the PWA design quality with enhanced native features.

Author: DarkLightX/Dana Edwards
"""

import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font
from pathlib import Path
import threading
import json
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

class ModernTauTranslatorApp:
    """Modern professional GUI for TauTranslator with enhanced design."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_modern_window()
        self.setup_custom_styles()
        
        # Application state
        self.translator = None
        self.current_theme = "light"
        self.is_authenticated = False
        self.session_token = None
        self.active_grammar = None
        self.project_files = []
        self.translation_history = []
        
        # UI Components
        self.create_modern_ui()
        self.load_translator()
        self.apply_theme()
        
    def setup_modern_window(self):
        """Configure the main window with modern design."""
        self.root.title("Tau Translator Alpha")
        
        # Set window size and center
        window_width = 1600
        window_height = 900
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1200, 700)
        
        # Modern color palette
        self.colors = {
            'light': {
                'bg': '#f4f7f9',
                'fg': '#333333',
                'primary': '#0070f3',
                'primary_hover': '#0056b3',
                'secondary': '#6c757d',
                'success': '#28a745',
                'success_hover': '#218838',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'card_bg': '#ffffff',
                'card_border': '#e0e0e0',
                'input_bg': '#ffffff',
                'input_border': '#ced4da',
                'header_bg': '#ffffff',
                'sidebar_bg': '#f8f9fa',
                'text_primary': '#212529',
                'text_secondary': '#6c757d',
                'text_muted': '#868e96',
                'shadow': '#00000010'
            },
            'dark': {
                'bg': '#1a1a1a',
                'fg': '#f0f0f0',
                'primary': '#007bff',
                'primary_hover': '#0069d9',
                'secondary': '#888888',
                'success': '#28a745',
                'success_hover': '#34ce57',
                'danger': '#f44336',
                'warning': '#ff9800',
                'info': '#2196f3',
                'card_bg': '#2c2c2c',
                'card_border': '#444444',
                'input_bg': '#363636',
                'input_border': '#555555',
                'header_bg': '#222222',
                'sidebar_bg': '#252525',
                'text_primary': '#e0e0e0',
                'text_secondary': '#999999',
                'text_muted': '#666666',
                'shadow': '#00000050'
            }
        }
        
        # Configure window for better appearance
        self.root.configure(bg=self.colors['light']['bg'])
        
        # Platform-specific enhancements
        if sys.platform == 'darwin':  # macOS
            self.root.createcommand('tk::mac::ShowPreferences', self.show_preferences)
            
    def setup_custom_styles(self):
        """Setup custom ttk styles for modern appearance."""
        self.style = ttk.Style()
        
        # Configure custom fonts
        self.fonts = {
            'heading': font.Font(family='SF Pro Display' if sys.platform == 'darwin' else 'Segoe UI', 
                               size=24, weight='bold'),
            'subheading': font.Font(family='SF Pro Display' if sys.platform == 'darwin' else 'Segoe UI', 
                                  size=16, weight='normal'),
            'body': font.Font(family='SF Pro Text' if sys.platform == 'darwin' else 'Segoe UI', 
                            size=13),
            'code': font.Font(family='SF Mono' if sys.platform == 'darwin' else 'Consolas', 
                            size=12),
            'small': font.Font(family='SF Pro Text' if sys.platform == 'darwin' else 'Segoe UI', 
                             size=11)
        }
        
    def create_modern_ui(self):
        """Create the modern professional UI."""
        # Main container
        self.main_container = tk.Frame(self.root, bg=self.colors['light']['bg'])
        self.main_container.pack(fill='both', expand=True)
        
        # Create components
        self.create_header()
        self.create_content_area()
        self.create_status_bar()
        
    def create_header(self):
        """Create modern header with navigation."""
        header = tk.Frame(self.main_container, bg=self.colors['light']['header_bg'], height=60)
        header.pack(fill='x', side='top')
        header.pack_propagate(False)
        
        # Add shadow effect
        shadow = tk.Frame(self.main_container, bg=self.colors['light']['card_border'], height=1)
        shadow.pack(fill='x', side='top')
        
        # Header content
        header_content = tk.Frame(header, bg=self.colors['light']['header_bg'])
        header_content.pack(fill='both', expand=True, padx=20)
        
        # Logo and title
        logo_frame = tk.Frame(header_content, bg=self.colors['light']['header_bg'])
        logo_frame.pack(side='left', fill='y')
        
        title = tk.Label(logo_frame, text="TauTranslator", 
                        font=self.fonts['heading'],
                        fg=self.colors['light']['primary'],
                        bg=self.colors['light']['header_bg'])
        title.pack(side='left', pady=10)
        
        subtitle = tk.Label(logo_frame, text="Alpha", 
                          font=self.fonts['small'],
                          fg=self.colors['light']['text_secondary'],
                          bg=self.colors['light']['header_bg'])
        subtitle.pack(side='left', padx=(10, 0), pady=10)
        
        # Right side controls
        controls_frame = tk.Frame(header_content, bg=self.colors['light']['header_bg'])
        controls_frame.pack(side='right', fill='y')
        
        # Theme toggle
        self.theme_btn = self.create_icon_button(
            controls_frame, "🌙" if self.current_theme == "light" else "☀️",
            self.toggle_theme, "Toggle theme"
        )
        self.theme_btn.pack(side='left', padx=5)
        
        # Authentication status
        self.auth_frame = tk.Frame(controls_frame, bg=self.colors['light']['header_bg'])
        self.auth_frame.pack(side='left', padx=(20, 10))
        
        self.auth_indicator = tk.Label(
            self.auth_frame, text="●", font=('Arial', 12),
            fg=self.colors['light']['danger'],
            bg=self.colors['light']['header_bg']
        )
        self.auth_indicator.pack(side='left', padx=(0, 5))
        
        self.auth_label = tk.Label(
            self.auth_frame, text="Not Authenticated",
            font=self.fonts['small'],
            fg=self.colors['light']['text_secondary'],
            bg=self.colors['light']['header_bg']
        )
        self.auth_label.pack(side='left')
        
        # Settings button
        settings_btn = self.create_icon_button(
            controls_frame, "⚙️", self.show_settings, "Settings"
        )
        settings_btn.pack(side='left', padx=5)
        
    def create_content_area(self):
        """Create the main content area with panels."""
        content = tk.Frame(self.main_container, bg=self.colors['light']['bg'])
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create three-column layout
        # Left sidebar
        self.create_sidebar(content)
        
        # Main editor area
        self.create_editor_area(content)
        
        # Right panel (properties/info)
        self.create_properties_panel(content)
        
    def create_sidebar(self, parent):
        """Create the left sidebar with file explorer."""
        sidebar = tk.Frame(parent, bg=self.colors['light']['sidebar_bg'], width=280)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # Apply rounded corners effect with border
        self.apply_card_style(sidebar)
        
        # Sidebar header
        header = tk.Frame(sidebar, bg=self.colors['light']['sidebar_bg'], height=50)
        header.pack(fill='x', padx=15, pady=(15, 0))
        
        tk.Label(header, text="Project Explorer", 
                font=self.fonts['subheading'],
                fg=self.colors['light']['text_primary'],
                bg=self.colors['light']['sidebar_bg']).pack(side='left')
        
        # File tree placeholder
        tree_frame = tk.Frame(sidebar, bg=self.colors['light']['sidebar_bg'])
        tree_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.file_tree = ttk.Treeview(tree_frame, show='tree', selectmode='browse')
        self.file_tree.pack(fill='both', expand=True)
        
        # Add some sample items
        self.file_tree.insert('', 'end', 'project', text='📁 TauProject', open=True)
        self.file_tree.insert('project', 'end', text='📄 main.tau')
        self.file_tree.insert('project', 'end', text='📄 rules.tce')
        self.file_tree.insert('project', 'end', text='📄 config.json')
        
    def create_editor_area(self, parent):
        """Create the main editor area with split panes."""
        editor_container = tk.Frame(parent, bg=self.colors['light']['card_bg'])
        editor_container.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.apply_card_style(editor_container)
        
        # Editor header with controls
        header = tk.Frame(editor_container, bg=self.colors['light']['card_bg'], height=60)
        header.pack(fill='x', padx=20, pady=(15, 0))
        
        # Translation controls
        controls = tk.Frame(header, bg=self.colors['light']['card_bg'])
        controls.pack(fill='x')
        
        tk.Label(controls, text="Translate from", 
                font=self.fonts['body'],
                fg=self.colors['light']['text_secondary'],
                bg=self.colors['light']['card_bg']).pack(side='left', padx=(0, 10))
        
        self.source_format = ttk.Combobox(
            controls, values=['Natural Language', 'Tau Language', 'TCE'],
            font=self.fonts['body'], width=20, state='readonly'
        )
        self.source_format.set('Natural Language')
        self.source_format.pack(side='left', padx=(0, 20))
        
        tk.Label(controls, text="to", 
                font=self.fonts['body'],
                fg=self.colors['light']['text_secondary'],
                bg=self.colors['light']['card_bg']).pack(side='left', padx=(0, 10))
        
        self.target_format = ttk.Combobox(
            controls, values=['Tau Language', 'TCE', 'ILR'],
            font=self.fonts['body'], width=20, state='readonly'
        )
        self.target_format.set('Tau Language')
        self.target_format.pack(side='left', padx=(0, 20))
        
        # Translate button
        self.translate_btn = tk.Button(
            controls, text="Translate →", 
            font=self.fonts['body'], 
            bg=self.colors['light']['success'],
            fg='white',
            bd=0, padx=25, pady=8,
            cursor='hand2',
            command=self.translate
        )
        self.translate_btn.pack(side='left')
        self.bind_hover(self.translate_btn, self.colors['light']['success'], 
                        self.colors['light']['success_hover'])
        
        # Editor panes
        panes_container = tk.Frame(editor_container, bg=self.colors['light']['card_bg'])
        panes_container.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Input pane
        input_frame = tk.Frame(panes_container, bg=self.colors['light']['card_bg'])
        input_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(input_frame, text="Input", 
                font=self.fonts['body'],
                fg=self.colors['light']['text_secondary'],
                bg=self.colors['light']['card_bg']).pack(anchor='w', pady=(0, 5))
        
        self.input_text = self.create_text_editor(input_frame)
        self.input_text.pack(fill='both', expand=True)
        
        # Output pane
        output_frame = tk.Frame(panes_container, bg=self.colors['light']['card_bg'])
        output_frame.pack(side='left', fill='both', expand=True)
        
        tk.Label(output_frame, text="Output", 
                font=self.fonts['body'],
                fg=self.colors['light']['text_secondary'],
                bg=self.colors['light']['card_bg']).pack(anchor='w', pady=(0, 5))
        
        self.output_text = self.create_text_editor(output_frame, readonly=True)
        self.output_text.pack(fill='both', expand=True)
        
    def create_properties_panel(self, parent):
        """Create the right properties/info panel."""
        panel = tk.Frame(parent, bg=self.colors['light']['card_bg'], width=320)
        panel.pack(side='right', fill='y')
        panel.pack_propagate(False)
        
        self.apply_card_style(panel)
        
        # Panel content with tabs
        notebook = ttk.Notebook(panel)
        notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Grammar tab
        grammar_tab = tk.Frame(notebook, bg=self.colors['light']['card_bg'])
        notebook.add(grammar_tab, text='Grammar')
        
        grammar_content = tk.Frame(grammar_tab, bg=self.colors['light']['card_bg'])
        grammar_content.pack(fill='both', expand=True, padx=10, pady=10)
        
        tk.Label(grammar_content, text="Active Grammar", 
                font=self.fonts['body'],
                fg=self.colors['light']['text_primary'],
                bg=self.colors['light']['card_bg']).pack(anchor='w', pady=(0, 10))
        
        self.grammar_status = tk.Label(
            grammar_content, text="No grammar loaded",
            font=self.fonts['small'],
            fg=self.colors['light']['text_secondary'],
            bg=self.colors['light']['card_bg']
        )
        self.grammar_status.pack(anchor='w')
        
        # History tab
        history_tab = tk.Frame(notebook, bg=self.colors['light']['card_bg'])
        notebook.add(history_tab, text='History')
        
        # Validation tab
        validation_tab = tk.Frame(notebook, bg=self.colors['light']['card_bg'])
        notebook.add(validation_tab, text='Validation')
        
    def create_status_bar(self):
        """Create the bottom status bar."""
        status_bar = tk.Frame(self.main_container, bg=self.colors['light']['card_border'], height=30)
        status_bar.pack(fill='x', side='bottom')
        status_bar.pack_propagate(False)
        
        status_content = tk.Frame(status_bar, bg=self.colors['light']['card_border'])
        status_content.pack(fill='both', expand=True, padx=20)
        
        # Left side - status message
        self.status_label = tk.Label(
            status_content, text="Ready",
            font=self.fonts['small'],
            fg=self.colors['light']['text_secondary'],
            bg=self.colors['light']['card_border']
        )
        self.status_label.pack(side='left', pady=5)
        
        # Right side - statistics
        stats_frame = tk.Frame(status_content, bg=self.colors['light']['card_border'])
        stats_frame.pack(side='right', pady=5)
        
        self.stats_label = tk.Label(
            stats_frame, text="Translations: 0 | Session: 0m",
            font=self.fonts['small'],
            fg=self.colors['light']['text_secondary'],
            bg=self.colors['light']['card_border']
        )
        self.stats_label.pack()
        
    def create_text_editor(self, parent, readonly=False):
        """Create a styled text editor widget."""
        frame = tk.Frame(parent, bg=self.colors['light']['input_border'], bd=1)
        
        text = scrolledtext.ScrolledText(
            frame,
            font=self.fonts['code'],
            bg=self.colors['light']['input_bg'],
            fg=self.colors['light']['text_primary'],
            insertbackground=self.colors['light']['primary'],
            selectbackground=self.colors['light']['primary'],
            selectforeground='white',
            wrap=tk.WORD,
            padx=15,
            pady=15,
            relief='flat',
            borderwidth=0
        )
        text.pack(fill='both', expand=True)
        
        if readonly:
            text.config(state='disabled')
            
        return frame
        
    def create_icon_button(self, parent, icon, command, tooltip=None):
        """Create a modern icon button."""
        btn = tk.Button(
            parent, text=icon,
            font=('Arial', 16),
            bg=self.colors['light']['header_bg'],
            fg=self.colors['light']['text_primary'],
            bd=0, padx=10, pady=5,
            cursor='hand2',
            command=command
        )
        
        if tooltip:
            self.create_tooltip(btn, tooltip)
            
        return btn
        
    def apply_card_style(self, widget):
        """Apply card-like styling to a widget."""
        widget.config(
            bg=self.colors['light']['card_bg'],
            highlightbackground=self.colors['light']['card_border'],
            highlightthickness=1,
            relief='flat'
        )
        
    def bind_hover(self, widget, normal_bg, hover_bg):
        """Bind hover effects to a widget."""
        def on_enter(e):
            widget.config(bg=hover_bg)
            
        def on_leave(e):
            widget.config(bg=normal_bg)
            
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget."""
        def on_enter(e):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{e.x_root+10}+{e.y_root+10}")
            
            label = tk.Label(
                tooltip, text=text,
                font=self.fonts['small'],
                bg=self.colors['light']['text_primary'],
                fg=self.colors['light']['card_bg'],
                padx=8, pady=4
            )
            label.pack()
            
            widget.tooltip = tooltip
            
        def on_leave(e):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
                
        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)
        
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.theme_btn.config(text="☀️" if self.current_theme == "dark" else "🌙")
        
    def apply_theme(self):
        """Apply the current theme to all widgets."""
        theme = self.colors[self.current_theme]
        
        # This would recursively update all widget colors
        # For brevity, showing the concept
        self.root.config(bg=theme['bg'])
        self.main_container.config(bg=theme['bg'])
        
        self.update_status(f"Theme changed to {self.current_theme}")
        
    def show_settings(self):
        """Show settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("600x400")
        settings_window.configure(bg=self.colors[self.current_theme]['card_bg'])
        
        # Settings content
        tk.Label(
            settings_window, 
            text="Settings",
            font=self.fonts['heading'],
            bg=self.colors[self.current_theme]['card_bg'],
            fg=self.colors[self.current_theme]['text_primary']
        ).pack(pady=20)
        
    def show_preferences(self):
        """Show preferences (macOS menu integration)."""
        self.show_settings()
        
    def translate(self):
        """Perform translation."""
        source_text = self.input_text.winfo_children()[0].get('1.0', tk.END).strip()
        
        if not source_text:
            messagebox.showwarning("Input Required", "Please enter text to translate")
            return
            
        self.update_status("Translating...")
        self.translate_btn.config(state='disabled', text="Translating...")
        
        # Simulate translation (would call actual translator)
        def do_translate():
            import time
            time.sleep(1)  # Simulate processing
            
            # Mock result
            result = f"// Translated from {self.source_format.get()} to {self.target_format.get()}\n"
            result += f"// Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            if self.target_format.get() == "Tau Language":
                result += "r system_rule[t] = input[t] > threshold\n"
                result += "always (system_rule[t] -> alert[t])"
            else:
                result += "The system rule states that when input exceeds threshold, an alert is triggered."
                
            self.root.after(0, self.display_result, result)
            
        threading.Thread(target=do_translate, daemon=True).start()
        
    def display_result(self, result):
        """Display translation result."""
        output_widget = self.output_text.winfo_children()[0]
        output_widget.config(state='normal')
        output_widget.delete('1.0', tk.END)
        output_widget.insert('1.0', result)
        output_widget.config(state='disabled')
        
        self.translate_btn.config(state='normal', text="Translate →")
        self.update_status("Translation complete")
        
        # Update statistics
        self.translation_history.append({
            'timestamp': datetime.now(),
            'source': self.source_format.get(),
            'target': self.target_format.get()
        })
        self.update_stats()
        
    def update_status(self, message):
        """Update status bar message."""
        self.status_label.config(text=message)
        
    def update_stats(self):
        """Update statistics display."""
        count = len(self.translation_history)
        session_time = 0  # Would calculate actual session time
        self.stats_label.config(text=f"Translations: {count} | Session: {session_time}m")
        
    def load_translator(self):
        """Load the translator system."""
        def load():
            try:
                from tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator
                self.translator = LMQLBidirectionalTranslator()
                self.root.after(0, lambda: self.update_status("Translator loaded successfully"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.update_status(f"Failed to load translator: {error_msg}"))
                
        threading.Thread(target=load, daemon=True).start()
        
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Launch the modern GUI application."""
    print("🚀 Launching Tau Translator Alpha")
    print("Modern desktop interface with enhanced design")
    
    app = ModernTauTranslatorApp()
    app.run()


if __name__ == "__main__":
    main()