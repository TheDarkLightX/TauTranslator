#!/usr/bin/env python3
"""
TauTranslator PyQt6 Interface with AutoComplete
==============================================

Enhanced version with autocomplete functionality following 
the Intentional Disclosure Principle.

Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path
from typing import List, Optional
import requests

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QComboBox, QCompleter, 
    QListView, QSplitter, QFrame, QToolBar, QStatusBar
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QStringListModel,
    QAbstractListModel, QModelIndex
)
from PyQt6.QtGui import (
    QAction, QFont, QFontDatabase, QTextCharFormat, 
    QSyntaxHighlighter, QTextDocument, QTextCursor
)

# Import the original components
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
try:
    from tau_translator_desktop_qt import TauSyntaxHighlighter, TranslationWorker, TauTranslatorQt as _TauTranslatorQt
except Exception:
    # Fallback to classes from comprehensive module if direct import unavailable
    try:
        from .tau_translator_qt_educational_complete import TauSyntaxHighlighter, TranslationWorker  # type: ignore
    except Exception:
        TauSyntaxHighlighter, TranslationWorker = None, None  # type: ignore
    _TauTranslatorQt = None


class AutoCompleteSuggestion:
    """Domain type for autocomplete suggestions."""
    def __init__(self, text: str, type: str, description: str = ""):
        self.text = text
        self.type = type
        self.description = description


class AutoCompleteService:
    """Service for fetching autocomplete suggestions (Rule 4: Isolate Impurity)."""
    
    @staticmethod
    async def fetch_suggestions_from_backend_async(text: str, language: str) -> List[AutoCompleteSuggestion]:
        """Fetch suggestions from backend API."""
        try:
            response = requests.post(
                'http://localhost:8000/api/nlp/autocomplete',
                json={'text': text, 'language': language},
                timeout=1.0
            )
            
            if response.ok:
                data = response.json()
                if data.get('success'):
                    return [
                        AutoCompleteSuggestion(
                            s['text'], 
                            s.get('type', 'unknown'),
                            s.get('description', '')
                        )
                        for s in data['data']['suggestions']
                    ]
        except:
            pass
        
        # Return fallback suggestions
        return AutoCompleteService._generate_fallback_suggestions(text, language)
    
    @staticmethod
    def _generate_fallback_suggestions(text: str, language: str) -> List[AutoCompleteSuggestion]:
        """Generate basic suggestions when backend unavailable."""
        if language != "TAU":
            return []
        
        tau_keywords = [
            AutoCompleteSuggestion('always', 'temporal', 'Temporal operator: always true'),
            AutoCompleteSuggestion('sometimes', 'temporal', 'Temporal operator: sometimes true'),
            AutoCompleteSuggestion('eventually', 'temporal', 'Temporal operator: eventually true'),
            AutoCompleteSuggestion('never', 'temporal', 'Temporal operator: never true'),
            AutoCompleteSuggestion('forall', 'quantifier', 'Universal quantification'),
            AutoCompleteSuggestion('exists', 'quantifier', 'Existential quantification'),
            AutoCompleteSuggestion('DEFINE', 'keyword', 'Define a new concept'),
            AutoCompleteSuggestion(':=', 'operator', 'Definition operator'),
            AutoCompleteSuggestion('->', 'operator', 'Implication operator'),
            AutoCompleteSuggestion('<->', 'operator', 'Equivalence operator'),
        ]
        
        # Filter by prefix
        prefix = text.lower()
        return [s for s in tau_keywords if s.text.lower().startswith(prefix)][:5]


class CodeEditorWithAutoComplete(QTextEdit):
    """Enhanced code editor with autocomplete functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        
        # Initialize autocomplete
        self.completer = None
        self.autocomplete_timer = QTimer()
        self.autocomplete_timer.timeout.connect(self._fetch_suggestions_async)
        self.autocomplete_timer.setSingleShot(True)
        
        self.current_language = "PLAIN_ENGLISH"
        self.highlighter = None
        
        # Autocomplete state
        self.last_request_text = ""
        self.is_fetching = False
        
    def set_language(self, language: str):
        """Set the current language for syntax highlighting and autocomplete."""
        self.current_language = language
        
        # Enable syntax highlighting for TAU
        if language == "TAU" and not self.highlighter:
            self.highlighter = TauSyntaxHighlighter(self.document())
        elif language != "TAU" and self.highlighter:
            self.highlighter = None
        
        # Setup completer for TAU and CNL
        if language in ["TAU", "CNL"]:
            self._setup_completer()
        else:
            self._remove_completer()
    
    def _setup_completer(self):
        """Initialize the completer widget."""
        if not self.completer:
            self.completer = QCompleter()
            self.completer.setWidget(self)
            self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
            self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            self.completer.activated.connect(self._insert_completion)
            
            # Style the popup
            popup = self.completer.popup()
            popup.setStyleSheet("""
                QListView {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 4px;
                    padding: 4px;
                    selection-background-color: #0070f3;
                    selection-color: white;
                }
                QListView::item {
                    padding: 4px;
                    border-radius: 2px;
                }
                QListView::item:hover {
                    background-color: #f0f0f0;
                }
            """)
    
    def _remove_completer(self):
        """Remove completer when not needed."""
        if self.completer:
            self.completer.setWidget(None)
            self.completer = None
    
    def keyPressEvent(self, event):
        """Handle key press events for autocomplete."""
        if self.completer and self.completer.popup().isVisible():
            # Handle navigation in completer
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                event.ignore()
                return
            elif event.key() == Qt.Key.Key_Escape:
                self.completer.popup().hide()
                event.ignore()
                return
        
        # Process the key press
        super().keyPressEvent(event)
        
        # Trigger autocomplete for TAU/CNL
        if self.current_language in ["TAU", "CNL"] and self.completer:
            # Don't trigger on navigation keys
            if event.key() not in (Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right):
                self._trigger_autocomplete()
    
    def _trigger_autocomplete(self):
        """Trigger autocomplete after a delay."""
        self.autocomplete_timer.stop()
        self.autocomplete_timer.start(300)  # 300ms debounce
    
    def _fetch_suggestions_async(self):
        """Fetch autocomplete suggestions (async simulation)."""
        if self.is_fetching:
            return
        
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        if not word or len(word) < 1:
            if self.completer:
                self.completer.popup().hide()
            return
        
        if word == self.last_request_text:
            return
        
        self.last_request_text = word
        self.is_fetching = True
        
        # Fetch suggestions (synchronous for simplicity)
        suggestions = AutoCompleteService._generate_fallback_suggestions(word, self.current_language)
        
        if suggestions:
            # Update completer model
            suggestion_texts = [s.text for s in suggestions]
            model = QStringListModel(suggestion_texts)
            self.completer.setModel(model)
            
            # Position and show popup
            cursor_rect = self.cursorRect()
            cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0) + 
                               self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cursor_rect)
            
            # Set prefix
            self.completer.setCompletionPrefix(word)
        else:
            self.completer.popup().hide()
        
        self.is_fetching = False
    
    def _insert_completion(self, completion):
        """Insert the selected completion."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        cursor.insertText(completion)
        self.setTextCursor(cursor)


class TauTranslatorQtAutoComplete(QMainWindow):
    """Enhanced Tau Translator with AutoComplete."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tau Translator with AutoComplete")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Tau Translator with AutoComplete"))
        layout.addLayout(header_layout)
        
        # Control bar
        control_layout = QHBoxLayout()
        
        # Language selectors
        self.left_language = QComboBox()
        self.left_language.addItems(['PLAIN_ENGLISH', 'TAU', 'CNL', 'ILR'])
        self.left_language.currentTextChanged.connect(self._on_left_language_changed)
        
        self.right_language = QComboBox()
        self.right_language.addItems(['TAU', 'PLAIN_ENGLISH', 'CNL', 'ILR'])
        self.right_language.currentTextChanged.connect(self._on_right_language_changed)
        
        # Buttons
        self.swap_button = QPushButton("⇄ Swap")
        self.swap_button.clicked.connect(self._swap_languages)
        
        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self._translate)
        self.translate_button.setStyleSheet("""
            QPushButton {
                background-color: #0070f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0051cc;
            }
        """)
        
        control_layout.addWidget(QLabel("From:"))
        control_layout.addWidget(self.left_language)
        control_layout.addWidget(self.swap_button)
        control_layout.addWidget(QLabel("To:"))
        control_layout.addWidget(self.right_language)
        control_layout.addStretch()
        control_layout.addWidget(self.translate_button)
        
        layout.addLayout(control_layout)
        
        # Editor panels
        editor_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left editor
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.Box)
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("Input"))
        self.left_editor = CodeEditorWithAutoComplete()
        self.left_editor.setPlaceholderText("Enter text here... (AutoComplete enabled for TAU/CNL)")
        left_layout.addWidget(self.left_editor)
        
        # Right editor
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.Box)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("Output"))
        self.right_editor = CodeEditorWithAutoComplete()
        self.right_editor.setPlaceholderText("Translation will appear here...")
        right_layout.addWidget(self.right_editor)
        
        editor_splitter.addWidget(left_frame)
        editor_splitter.addWidget(right_frame)
        layout.addWidget(editor_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. AutoComplete enabled for TAU and CNL.")
        
        # Initialize language settings
        self._on_left_language_changed(self.left_language.currentText())
        self._on_right_language_changed(self.right_language.currentText())
    
    def _on_left_language_changed(self, language):
        """Handle left language change."""
        self.left_editor.set_language(language)
        if language in ["TAU", "CNL"]:
            self.status_bar.showMessage(f"AutoComplete enabled for {language}", 2000)
    
    def _on_right_language_changed(self, language):
        """Handle right language change."""
        self.right_editor.set_language(language)
    
    def _swap_languages(self):
        """Swap languages and text."""
        # Swap languages
        left_lang = self.left_language.currentText()
        right_lang = self.right_language.currentText()
        self.left_language.setCurrentText(right_lang)
        self.right_language.setCurrentText(left_lang)
        
        # Swap text
        left_text = self.left_editor.toPlainText()
        right_text = self.right_editor.toPlainText()
        self.left_editor.setPlainText(right_text)
        self.right_editor.setPlainText(left_text)
    
    def _translate(self):
        """Perform translation."""
        source_text = self.left_editor.toPlainText()
        if not source_text.strip():
            self.status_bar.showMessage("Please enter text to translate", 3000)
            return
        
        # Mock translation for demo
        self.status_bar.showMessage("Translating...", 0)
        QTimer.singleShot(500, lambda: self._show_translation(f"// Translated from {self.left_language.currentText()} to {self.right_language.currentText()}\n{source_text}"))
    
    def _show_translation(self, result):
        """Show translation result."""
        self.right_editor.setPlainText(result)
        self.status_bar.showMessage("Translation complete", 3000)


# Provide a compatibility alias if tests import TauTranslatorQt from this module
TauTranslatorQt = TauTranslatorQtAutoComplete if _TauTranslatorQt is None else _TauTranslatorQt


def main():
    """Run the enhanced application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tau Translator AutoComplete")
    
    window = TauTranslatorQtAutoComplete()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()