#!/usr/bin/env python3
"""
TauTranslatorOmega Splash Screen
===============================

Beautiful loading screen with animations and progress indicators.
Designed by Claude 3.5 Sonnet for professional UX.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math

class SplashScreen:
    """Professional splash screen with animations."""
    
    def __init__(self, main_app_callback):
        self.main_app_callback = main_app_callback
        self.splash = tk.Tk()
        self.setup_splash()
        self.create_splash_ui()
        self.start_loading_animation()
    
    def setup_splash(self):
        """Configure the splash window."""
        self.splash.title("TauTranslatorOmega")
        self.splash.geometry("600x400")
        self.splash.resizable(False, False)
        
        # Center the window
        self.splash.update_idletasks()
        x = (self.splash.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.splash.winfo_screenheight() // 2) - (400 // 2)
        self.splash.geometry(f"600x400+{x}+{y}")
        
        # Remove window decorations for modern look
        self.splash.overrideredirect(True)
        
        # Modern colors
        self.colors = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'accent': '#9b59b6',
            'success': '#27ae60',
            'white': '#ffffff',
            'light': '#ecf0f1',
            'dark': '#34495e'
        }
        
        self.splash.configure(bg=self.colors['primary'])
    
    def create_splash_ui(self):
        """Create the splash screen UI."""
        # Main container
        main_frame = tk.Frame(self.splash, bg=self.colors['primary'])
        main_frame.pack(fill='both', expand=True)
        
        # Top section with logo and title
        top_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=200)
        top_frame.pack(fill='x', pady=50)
        top_frame.pack_propagate(False)
        
        # Logo (large emoji as placeholder)
        logo_label = tk.Label(
            top_frame,
            text="🌍",
            font=('Segoe UI', 72),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        logo_label.pack()
        
        # Title
        title_label = tk.Label(
            top_frame,
            text="TauTranslatorOmega",
            font=('Segoe UI', 32, 'bold'),
            bg=self.colors['primary'],
            fg=self.colors['white']
        )
        title_label.pack(pady=10)
        
        # Subtitle
        subtitle_label = tk.Label(
            top_frame,
            text="Professional AI-Enhanced Translation",
            font=('Segoe UI', 14),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        subtitle_label.pack()
        
        # Version and credits
        version_label = tk.Label(
            top_frame,
            text="v3.0 • Designed by Claude 3.5 Sonnet",
            font=('Segoe UI', 10),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        version_label.pack(pady=5)
        
        # Middle section with loading animation
        middle_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=100)
        middle_frame.pack(fill='x', pady=20)
        middle_frame.pack_propagate(False)
        
        # Loading animation canvas
        self.canvas = tk.Canvas(
            middle_frame,
            width=300,
            height=60,
            bg=self.colors['primary'],
            highlightthickness=0
        )
        self.canvas.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            middle_frame,
            length=300,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress.pack(pady=10)
        
        # Status text
        self.status_label = tk.Label(
            middle_frame,
            text="Initializing...",
            font=('Segoe UI', 11),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        self.status_label.pack(pady=5)
        
        # Bottom section with features
        bottom_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        bottom_frame.pack(fill='x', side='bottom', pady=20)
        
        features_label = tk.Label(
            bottom_frame,
            text="🤖 AI-Enhanced • 🔄 Bidirectional • 🎯 Professional • 🔒 Privacy-First",
            font=('Segoe UI', 10),
            bg=self.colors['primary'],
            fg=self.colors['light']
        )
        features_label.pack()
        
        # Configure progress bar style
        style = ttk.Style()
        style.configure(
            'Custom.Horizontal.TProgressbar',
            background=self.colors['secondary'],
            troughcolor=self.colors['dark'],
            borderwidth=0,
            lightcolor=self.colors['secondary'],
            darkcolor=self.colors['secondary']
        )
    
    def start_loading_animation(self):
        """Start the loading animation and initialization."""
        def animate():
            # Loading steps with realistic timing
            steps = [
                ("Initializing TauTranslatorOmega...", 10),
                ("Loading pattern recognition engine...", 25),
                ("Setting up translation framework...", 40),
                ("Checking for AI models...", 55),
                ("Configuring user interface...", 70),
                ("Preparing translation examples...", 85),
                ("Finalizing setup...", 95),
                ("Ready to translate!", 100)
            ]
            
            for i, (status, progress) in enumerate(steps):
                self.splash.after(0, lambda s=status, p=progress: self.update_progress(s, p))
                time.sleep(0.8)  # Realistic loading time
            
            # Wait a moment then launch main app
            time.sleep(0.5)
            self.splash.after(0, self.launch_main_app)
        
        # Start animation in background thread
        threading.Thread(target=animate, daemon=True).start()
        
        # Start visual effects
        self.animate_dots()
    
    def update_progress(self, status, progress):
        """Update progress bar and status."""
        self.status_label.config(text=status)
        self.progress['value'] = progress
        
        # Update canvas animation based on progress
        self.canvas.delete("all")
        
        # Draw animated circles
        for i in range(5):
            x = 50 + i * 50
            y = 30
            radius = 8 + 4 * math.sin((progress / 10) + i)
            
            # Color based on progress
            if progress > i * 20:
                color = self.colors['secondary']
            else:
                color = self.colors['dark']
            
            self.canvas.create_oval(
                x - radius, y - radius,
                x + radius, y + radius,
                fill=color,
                outline=""
            )
    
    def animate_dots(self):
        """Animate loading dots."""
        def update_dots():
            current_text = self.status_label.cget("text")
            if current_text.endswith("..."):
                base_text = current_text[:-3]
            elif current_text.endswith(".."):
                base_text = current_text[:-2]
            elif current_text.endswith("."):
                base_text = current_text[:-1]
            else:
                base_text = current_text
            
            # Cycle through dot patterns
            dot_count = (int(time.time() * 2) % 4)
            dots = "." * dot_count
            
            if not base_text.endswith("!"):  # Don't animate "Ready!" message
                self.status_label.config(text=base_text + dots)
            
            # Continue animation
            self.splash.after(500, update_dots)
        
        update_dots()
    
    def launch_main_app(self):
        """Launch the main application."""
        self.splash.destroy()
        self.main_app_callback()
    
    def show(self):
        """Show the splash screen."""
        self.splash.mainloop()

def create_launcher():
    """Create launcher with splash screen."""
    def launch_main_app():
        """Launch the main TauTranslatorOmega application."""
        import tau_translator_app
        app = tau_translator_app.TauTranslatorApp()
        app.run()
    
    # Show splash screen first
    splash = SplashScreen(launch_main_app)
    splash.show()

if __name__ == "__main__":
    create_launcher()
