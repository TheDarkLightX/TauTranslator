#!/usr/bin/env python3
"""
TauTranslatorOmega UI Evolution Demo
===================================

Shows the evolution from original → modern → improved versions.
Demonstrates the iterative improvement process.
"""

import sys
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess
import threading

class UIEvolutionDemo:
    """Demo showing UI evolution across three versions."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_ui()
    
    def setup_window(self):
        """Setup the demo window."""
        self.root.title("TauTranslatorOmega - UI Evolution Demo")
        self.root.geometry("1400x900")
        self.root.configure(bg="#f8f9fa")
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
    
    def create_ui(self):
        """Create the evolution demo UI."""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="🎨 TauTranslatorOmega UI Evolution",
            font=('Segoe UI', 24, 'bold'),
            bg="#2c3e50",
            fg="white"
        ).pack(expand=True)
        
        # Main content
        main_frame = tk.Frame(self.root, bg="#f8f9fa")
        main_frame.pack(fill='both', expand=True, padx=30, pady=30)
        
        # Evolution timeline
        timeline_frame = tk.Frame(main_frame, bg="#f8f9fa")
        timeline_frame.pack(fill='both', expand=True)
        
        # Four versions side by side
        versions_container = tk.Frame(timeline_frame, bg="#f8f9fa")
        versions_container.pack(fill='both', expand=True)

        self.create_version_card(versions_container, "v1", "Original UI",
                                "Basic tkinter interface", "#e74c3c",
                                self.launch_original, "tau_translator_app.py")

        self.create_version_card(versions_container, "v2", "Modern UI",
                                "2024 design attempt", "#f39c12",
                                self.launch_modern, "modern_tau_translator.py")

        self.create_version_card(versions_container, "v3", "Improved UI",
                                "Fixed theme & sizing", "#3498db",
                                self.launch_improved, "improved_tau_translator.py")

        self.create_version_card(versions_container, "v4", "Final UI",
                                "Resizable & optimized", "#27ae60",
                                self.launch_final, "final_tau_translator.py")
        
        # Bottom section
        self.create_bottom_section(main_frame)
    
    def create_version_card(self, parent, version, title, description, color, launch_func, filename):
        """Create a version comparison card."""
        card_frame = tk.Frame(parent, bg="white", relief='solid', bd=1)
        card_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Header
        header = tk.Frame(card_frame, bg=color, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text=f"{version}: {title}",
            font=('Segoe UI', 16, 'bold'),
            bg=color,
            fg="white"
        ).pack(expand=True)
        
        # Content
        content = tk.Frame(card_frame, bg="white")
        content.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(
            content,
            text=description,
            font=('Segoe UI', 12),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=(0, 20))
        
        # Features based on version
        if version == "v1":
            features = [
                "• Basic tkinter styling",
                "• Cluttered toolbar",
                "• No theme support",
                "• Poor visual hierarchy",
                "• Static interface",
                "• Inconsistent spacing"
            ]
        elif version == "v2":
            features = [
                "• Modern color scheme",
                "• Card-based layout",
                "• Dark mode attempt",
                "• Better typography",
                "• Micro-interactions",
                "• ❌ Broken theme toggle",
                "• ❌ Font sizes too big",
                "• ❌ Button sizing issues"
            ]
        elif version == "v3":
            features = [
                "• ✅ Working dark/light mode",
                "• ✅ Proper font sizing",
                "• ✅ Better button proportions",
                "• ✅ Clean layout",
                "• ✅ Consistent theming",
                "• ⚠️ Fixed middle bar width"
            ]
        else:  # v4
            features = [
                "• ✅ Controls moved to top panel",
                "• ✅ Fully resizable layout",
                "• ✅ Better default window size",
                "• ✅ No cramped middle bar",
                "• ✅ Responsive design",
                "• ✅ Optimal user experience"
            ]
        
        for feature in features:
            color_fg = "#e74c3c" if "❌" in feature else "#27ae60" if "✅" in feature else "#6c757d"
            tk.Label(
                content,
                text=feature,
                font=('Segoe UI', 10),
                bg="white",
                fg=color_fg,
                justify='left'
            ).pack(anchor='w', pady=1)
        
        # Launch button
        tk.Button(
            content,
            text=f"🚀 Launch {version}",
            font=('Segoe UI', 12, 'bold'),
            bg=color,
            fg="white",
            relief='flat',
            padx=20,
            pady=10,
            command=launch_func,
            cursor='hand2'
        ).pack(pady=(20, 0))
        
        # Filename
        tk.Label(
            content,
            text=f"File: {filename}",
            font=('Segoe UI', 8),
            bg="white",
            fg="#999999"
        ).pack(pady=(10, 0))
    
    def create_bottom_section(self, parent):
        """Create bottom section with comparison tools."""
        bottom_frame = tk.Frame(parent, bg="white", relief='solid', bd=1)
        bottom_frame.pack(fill='x', pady=(30, 0))
        
        # Header
        header = tk.Frame(bottom_frame, bg="#3498db", height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="🔧 Comparison Tools",
            font=('Segoe UI', 16, 'bold'),
            bg="#3498db",
            fg="white"
        ).pack(expand=True)
        
        # Content
        content = tk.Frame(bottom_frame, bg="white")
        content.pack(fill='x', padx=20, pady=15)
        
        # Buttons
        button_frame = tk.Frame(content, bg="white")
        button_frame.pack()
        
        tk.Button(
            button_frame,
            text="👥 Launch All Three",
            font=('Segoe UI', 12, 'bold'),
            bg="#9b59b6",
            fg="white",
            relief='flat',
            padx=20,
            pady=10,
            command=self.launch_all,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="📊 Show Improvements",
            font=('Segoe UI', 12, 'bold'),
            bg="#16a085",
            fg="white",
            relief='flat',
            padx=20,
            pady=10,
            command=self.show_improvements,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="❌ Close Demo",
            font=('Segoe UI', 12, 'bold'),
            bg="#95a5a6",
            fg="white",
            relief='flat',
            padx=20,
            pady=10,
            command=self.root.quit,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def launch_original(self):
        """Launch original UI."""
        self.launch_version("tau_translator_app.py", "Original UI")
    
    def launch_modern(self):
        """Launch modern UI (with issues)."""
        self.launch_version("modern_tau_translator.py", "Modern UI (with issues)")
    
    def launch_improved(self):
        """Launch improved UI."""
        self.launch_version("improved_tau_translator.py", "Improved UI")

    def launch_final(self):
        """Launch final UI."""
        self.launch_version("final_tau_translator.py", "Final UI")
    
    def launch_version(self, filename, name):
        """Launch a specific version."""
        def run():
            try:
                subprocess.run([sys.executable, filename], cwd=Path(__file__).parent)
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to launch {name}: {e}"))
        
        threading.Thread(target=run, daemon=True).start()
        messagebox.showinfo("Launching", f"{name} is starting...")
    
    def launch_all(self):
        """Launch all three versions."""
        versions = [
            ("tau_translator_app.py", "Original"),
            ("modern_tau_translator.py", "Modern"),
            ("improved_tau_translator.py", "Improved")
        ]
        
        for filename, name in versions:
            def run(f=filename):
                try:
                    subprocess.run([sys.executable, f], cwd=Path(__file__).parent)
                except Exception as e:
                    print(f"Failed to launch {name}: {e}")
            
            threading.Thread(target=run, daemon=True).start()
        
        messagebox.showinfo("Launching", "All three versions are starting for comparison!")
    
    def show_improvements(self):
        """Show detailed improvements."""
        improvements_text = """
🎨 UI/UX Evolution Summary:

VERSION 1 (Original):
❌ Basic tkinter styling
❌ Cluttered interface
❌ No modern design principles

VERSION 2 (Modern Attempt):
⚠️ Attempted modern design
⚠️ Dark mode implementation (broken)
⚠️ Font sizes too large
⚠️ Button proportions poor

VERSION 3 (Improved):
✅ Working dark/light mode toggle
✅ Proper font sizing and hierarchy
✅ Better button proportions
✅ Clean, professional layout
✅ Consistent theming system
✅ Refined user experience

KEY IMPROVEMENTS:
• Fixed theme toggle functionality
• Reduced font sizes for better readability
• Improved button sizing and spacing
• Better color scheme implementation
• Cleaner code architecture
• Professional appearance

The evolution shows iterative improvement based on feedback!
        """
        
        messagebox.showinfo("UI/UX Improvements", improvements_text.strip())
    
    def run(self):
        """Run the evolution demo."""
        self.root.mainloop()

def main():
    """Launch the UI evolution demo."""
    print("🎨 TauTranslatorOmega UI Evolution Demo")
    print("Showing the iterative improvement process")
    
    demo = UIEvolutionDemo()
    demo.run()

if __name__ == "__main__":
    main()
