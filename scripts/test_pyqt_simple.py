#!/usr/bin/env python3
"""
Simple PyQt Test
===============

Minimal test to check if PyQt is working.

Copyright: DarkLightX/Dana Edwards
"""

import sys

print("Testing PyQt installation...")

# Try PyQt6 first
try:
    from PyQt6.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
    from PyQt6.QtCore import Qt
    pyqt_version = "PyQt6"
    print(f"✅ {pyqt_version} is available")
except ImportError:
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
        from PyQt5.QtCore import Qt
        pyqt_version = "PyQt5"
        print(f"✅ {pyqt_version} is available (fallback)")
    except ImportError:
        print("❌ No PyQt installation found!")
        print("\nInstall with:")
        print("  pip install PyQt6")
        print("  or")
        print("  pip install PyQt5")
        sys.exit(1)

# Create simple test window
class SimpleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"PyQt Test - {pyqt_version}")
        self.setGeometry(100, 100, 600, 400)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        
        # Label
        label = QLabel(f"✅ {pyqt_version} is working!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter if pyqt_version == "PyQt6" else Qt.AlignCenter)
        layout.addWidget(label)
        
        # Text editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type here to test...")
        layout.addWidget(self.editor)
        
        # Add some test text
        self.editor.setText("""TAU Test Examples:

1. Type: always
2. Type: forall
3. Type: exists

If you can see this window, PyQt is working correctly!
""")

print("Creating application...")
app = QApplication(sys.argv)

print("Creating window...")
window = SimpleWindow()
window.show()

print(f"✅ Window created successfully with {pyqt_version}")
print("\nIf the window doesn't appear, there may be a display issue.")
print("Press Ctrl+C to exit.")

sys.exit(app.exec() if pyqt_version == "PyQt6" else app.exec_())