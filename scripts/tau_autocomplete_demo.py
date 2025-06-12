#!/usr/bin/env python3
"""
TAU AutoComplete Demo
====================

A simple working demo of autocomplete for TAU language.

Copyright: DarkLightX/Dana Edwards
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QTextEdit, QLabel, QCompleter, QHBoxLayout, QPushButton
)
from PyQt6.QtCore import Qt, QTimer, QStringListModel
from PyQt6.QtGui import QTextCursor, QFont, QFontDatabase

class AutoCompleteTextEdit(QTextEdit):
    """Text editor with TAU autocomplete."""
    
    def __init__(self):
        super().__init__()
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(14)
        self.setFont(font)
        
        # TAU keywords and operators
        self.tau_suggestions = [
            "always", "sometimes", "eventually", "never",
            "forall", "exists", "DEFINE", "CONCEPT",
            "true", "false", "and", "or", "not",
            ":=", "->", "<->", "&&", "||", "!",
            "sbf", "ifile", "ofile", "console"
        ]
        
        # Setup completer
        self.completer = QCompleter(self.tau_suggestions)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)
        
        # Timer for debouncing
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_completions)
        self.timer.setSingleShot(True)
        
        self.setPlaceholderText("Start typing TAU code... Try 'al' for 'always', 'for' for 'forall', etc.")
    
    def keyPressEvent(self, event):
        """Handle key press events."""
        # If completer popup is visible, let it handle navigation
        if self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                event.ignore()
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.completer.popup().hide()
                event.accept()
                return
        
        # Normal key processing
        super().keyPressEvent(event)
        
        # Don't show completions for navigation keys
        if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
            return
        
        # Start timer for showing completions
        self.timer.stop()
        self.timer.start(200)  # 200ms delay
    
    def show_completions(self):
        """Show autocomplete suggestions."""
        # Get current word
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if len(word) < 1:
            self.completer.popup().hide()
            return
        
        # Filter suggestions
        filtered = [s for s in self.tau_suggestions if s.lower().startswith(word.lower())]
        
        if not filtered:
            self.completer.popup().hide()
            return
        
        # Update completer
        self.completer.setModel(QStringListModel(filtered))
        self.completer.setCompletionPrefix(word)
        
        # Position popup
        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(200)  # Fixed width for popup
        self.completer.complete(cursor_rect)
    
    def insert_completion(self, completion):
        """Insert selected completion."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertText(completion)
        self.setTextCursor(cursor)
        self.completer.popup().hide()


class AutoCompleteDemo(QMainWindow):
    """Main demo window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TAU AutoComplete Demo")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Layout
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("TAU Language AutoComplete Demo")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = header.font()
        font.setPointSize(16)
        font.setBold(True)
        header.setFont(font)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel(
            "Type TAU keywords to see autocomplete:\n"
            "• 'al' → always\n"
            "• 'for' → forall\n" 
            "• 'ex' → exists\n"
            "• ':' → :=\n"
            "• '-' → ->\n"
            "Use ↑↓ to navigate, Tab/Enter to accept, Esc to cancel"
        )
        instructions.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 10px; }")
        layout.addWidget(instructions)
        
        # Editor
        self.editor = AutoCompleteTextEdit()
        layout.addWidget(self.editor)
        
        # Button row
        button_layout = QHBoxLayout()
        
        # Example button
        example_btn = QPushButton("Load Example")
        example_btn.clicked.connect(self.load_example)
        button_layout.addWidget(example_btn)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.editor.clear)
        button_layout.addWidget(clear_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Status
        self.status = QLabel("Ready. Start typing to see autocomplete suggestions.")
        self.status.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.status)
    
    def load_example(self):
        """Load example TAU code."""
        example = """// TAU Example - Try typing more keywords!
DEFINE isEven(x) := exists k (x = 2 * k)

always (temperature > 30 -> coolingOn)
forall x (P(x) -> Q(x))
exists y (R(y) && S(y))

// Try typing:
// 'ev' for eventually
// 'so' for sometimes  
// 'ne' for never
"""
        self.editor.setPlainText(example)
        self.status.setText("Example loaded. Position cursor and continue typing to see autocomplete.")


def main():
    """Run the demo."""
    app = QApplication(sys.argv)
    
    demo = AutoCompleteDemo()
    demo.show()
    
    print("✅ TAU AutoComplete Demo is running!")
    print("The autocomplete should work when you type TAU keywords.")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()