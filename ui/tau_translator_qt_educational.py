#!/usr/bin/env python3
"""
TauTranslator PyQt6 Interface with Educational AutoComplete

Enhanced version with educational autocomplete functionality that
provides learning support, examples, and contextual hints.

Copyright: DarkLightX/Dana Edwards
"""

import sys
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import requests
from functools import lru_cache

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QComboBox, QCompleter, 
    QListWidget, QListWidgetItem, QSplitter, QFrame, QToolBar, 
    QStatusBar, QToolTip, QGroupBox, QCheckBox, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QStringListModel,
    QAbstractListModel, QModelIndex, QPoint, QRect
)
from PyQt6.QtGui import (
    QAction, QFont, QFontDatabase, QTextCharFormat, 
    QSyntaxHighlighter, QTextDocument, QTextCursor, QColor
)

# Import the original components
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from tau_translator_desktop_qt import TauSyntaxHighlighter, TranslationWorker


@dataclass
class EducationalSuggestion:
    """Domain type for educational autocomplete suggestions."""
    text: str
    display: str
    category: str
    difficulty: str
    description: str
    example: Optional[str] = None
    tau_equivalent: Optional[str] = None
    template: Optional[str] = None


class EducationalAutocompleteService:
    """Service for fetching educational autocomplete suggestions."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def fetch_suggestions(
        self, 
        text: str, 
        language: str = "TAU",
        learning_level: str = "intermediate",
        max_suggestions: int = 10
    ) -> tuple[List[EducationalSuggestion], Optional[str], Optional[str]]:
        """
        Fetch educational suggestions from backend.
        Returns (suggestions, context_hint, learning_tip)
        """
        if not text.strip():
            return [], None, None
        
        try:
            # Try educational endpoint first
            response = self.session.post(
                f"{self.base_url}/api/educational/autocomplete",
                json={
                    'text': text,
                    'language_mode': language,
                    'learning_level': learning_level,
                    'max_suggestions': max_suggestions,
                    'include_examples': True,
                    'include_templates': True
                },
                timeout=1.0
            )
            
            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    result = data['data']
                    suggestions = [
                        EducationalSuggestion(
                            text=s['text'],
                            display=s.get('display', s['text']),
                            category=s.get('category', 'unknown'),
                            difficulty=s.get('difficulty', 'intermediate'),
                            description=s.get('description', ''),
                            example=s.get('example'),
                            tau_equivalent=s.get('tau_equivalent'),
                            template=s.get('template')
                        )
                        for s in result.get('suggestions', [])
                    ]
                    
                    context_hint = result.get('context_hint')
                    learning_tip = result.get('learning_tip')
                    
                    return suggestions, context_hint, learning_tip
        
        except requests.exceptions.RequestException:
            pass
        
        # Fallback to basic endpoint
        try:
            response = self.session.post(
                f"{self.base_url}/api/nlp/autocomplete",
                json={'text': text, 'language': language},
                timeout=0.5
            )
            
            if response.ok:
                data = response.json()
                if data.get('status') == 'success':
                    suggestions = [
                        EducationalSuggestion(
                            text=s['text'],
                            display=s['text'],
                            category=s.get('type', 'unknown'),
                            difficulty='intermediate',
                            description=self._get_fallback_description(s['text'])
                        )
                        for s in data['data'].get('suggestions', [])
                    ]
                    return suggestions, None, None
        
        except requests.exceptions.RequestException:
            pass
        
        # Return offline suggestions
        return self._get_offline_suggestions(text, language), None, None
    
    @lru_cache(maxsize=100)
    def _get_fallback_description(self, keyword: str) -> str:
        """Get fallback description for keywords."""
        descriptions = {
            'always': 'Temporal operator: property holds at all times',
            'sometimes': 'Temporal operator: property holds at some time',
            'eventually': 'Temporal operator: property will hold in future',
            'never': 'Temporal operator: property never holds',
            'forall': 'Universal quantifier: for all values',
            'exists': 'Existential quantifier: for at least one value',
            'DEFINE': 'Define a new concept or function',
            ':=': 'Definition operator',
            '->': 'Implication: if-then',
            '<->': 'Equivalence: if and only if'
        }
        return descriptions.get(keyword, f'{keyword} operator')
    
    def _get_offline_suggestions(self, text: str, language: str) -> List[EducationalSuggestion]:
        """Generate offline suggestions when backend unavailable."""
        if language not in ["TAU", "TCE"]:
            return []
        
        suggestions = []
        
        if language == "TAU":
            tau_items = [
                ('always', 'temporal', 'Property holds at all times', 'always (x > 0)'),
                ('sometimes', 'temporal', 'Property holds at some time', 'sometimes (door_open)'),
                ('eventually', 'temporal', 'Property will hold', 'eventually (task_complete)'),
                ('forall', 'quantifier', 'For all values', 'forall x : x > 0 -> f(x) > 0'),
                ('exists', 'quantifier', 'For at least one value', 'exists x : x * x = 4'),
                ('solve', 'solver', 'Find solution', 'solve x = 0'),
                ('DEFINE', 'keyword', 'Define concept', 'DEFINE max(a,b) := a > b ? a : b')
            ]
            
            for keyword, category, desc, example in tau_items:
                if keyword.lower().startswith(text.lower()):
                    suggestions.append(EducationalSuggestion(
                        text=keyword,
                        display=keyword,
                        category=category,
                        difficulty='beginner' if category == 'keyword' else 'intermediate',
                        description=desc,
                        example=example
                    ))
        
        elif language == "TCE":
            tce_items = [
                ('for all ... such that ...', 'forall $x : $condition', 'Universal quantification'),
                ('there exists ... such that ...', 'exists $x : $condition', 'Existential quantification'),
                ('it is always the case that ...', 'always ($condition)', 'Temporal invariant'),
                ('if ... then ...', '$A -> $B', 'Logical implication')
            ]
            
            for pattern, tau_eq, desc in tce_items:
                if text.lower() in pattern.lower():
                    suggestions.append(EducationalSuggestion(
                        text=pattern,
                        display=pattern.replace('...', '___'),
                        category='pattern',
                        difficulty='intermediate',
                        description=desc,
                        tau_equivalent=tau_eq
                    ))
        
        return suggestions[:5]


class EducationalSuggestionWidget(QListWidget):
    """Custom widget for displaying educational suggestions."""
    
    suggestion_selected = pyqtSignal(EducationalSuggestion)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setMouseTracking(True)
        
        # Style the widget
        self.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 4px;
                border: 1px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #f0f7ff;
                border: 1px solid #0070f3;
            }
            QListWidget::item:selected {
                background-color: #0070f3;
                color: white;
            }
        """)
        
        self.suggestions = []
        self.itemClicked.connect(self._on_item_clicked)
    
    def show_suggestions(self, suggestions: List[EducationalSuggestion], at_point: QPoint):
        """Display suggestions at given point."""
        self.clear()
        self.suggestions = suggestions
        
        for i, suggestion in enumerate(suggestions):
            # Create rich item display
            item_text = f"{suggestion.display}"
            if suggestion.category:
                item_text += f" [{suggestion.category}]"
            
            item = QListWidgetItem(item_text)
            item.setToolTip(self._create_tooltip(suggestion))
            
            # Color code by difficulty
            if suggestion.difficulty == 'beginner':
                item.setForeground(QColor("#059862"))  # Green
            elif suggestion.difficulty == 'advanced':
                item.setForeground(QColor("#e11d48"))  # Red
            
            self.addItem(item)
        
        # Position and resize
        self.move(at_point)
        self.resize(400, min(len(suggestions) * 50 + 10, 300))
        self.show()
        
        # Select first item
        if self.count() > 0:
            self.setCurrentRow(0)
    
    def _create_tooltip(self, suggestion: EducationalSuggestion) -> str:
        """Create rich tooltip for suggestion."""
        parts = [f"<b>{suggestion.text}</b>"]
        
        if suggestion.description:
            parts.append(f"<br>{suggestion.description}")
        
        if suggestion.example:
            parts.append(f"<br><br><b>Example:</b><br><code>{suggestion.example}</code>")
        
        if suggestion.tau_equivalent:
            parts.append(f"<br><br><b>TAU:</b> <code>{suggestion.tau_equivalent}</code>")
        
        return "".join(parts)
    
    def _on_item_clicked(self, item):
        """Handle item click."""
        index = self.row(item)
        if 0 <= index < len(self.suggestions):
            self.suggestion_selected.emit(self.suggestions[index])
            self.hide()
    
    def get_selected_suggestion(self) -> Optional[EducationalSuggestion]:
        """Get currently selected suggestion."""
        current = self.currentRow()
        if 0 <= current < len(self.suggestions):
            return self.suggestions[current]
        return None


class CodeEditorWithEducationalAutoComplete(QTextEdit):
    """Enhanced code editor with educational autocomplete."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        
        # Initialize services
        self.autocomplete_service = EducationalAutocompleteService()
        self.suggestion_widget = EducationalSuggestionWidget(self)
        self.suggestion_widget.suggestion_selected.connect(self._insert_suggestion)
        self.suggestion_widget.hide()
        
        # Autocomplete state
        self.autocomplete_timer = QTimer()
        self.autocomplete_timer.timeout.connect(self._fetch_suggestions)
        self.autocomplete_timer.setSingleShot(True)
        
        self.current_language = "PLAIN_ENGLISH"
        self.learning_level = "intermediate"
        self.highlighter = None
        
        # Status display
        self.context_hint = ""
        self.learning_tip = ""
    
    def set_language(self, language: str):
        """Set current language for autocomplete and highlighting."""
        self.current_language = language
        
        # Enable syntax highlighting for TAU
        if language == "TAU" and not self.highlighter:
            self.highlighter = TauSyntaxHighlighter(self.document())
        elif language != "TAU" and self.highlighter:
            self.highlighter = None
    
    def set_learning_level(self, level: str):
        """Set learning level for suggestions."""
        self.learning_level = level
    
    def keyPressEvent(self, event):
        """Handle key press events for autocomplete."""
        # Handle suggestion widget navigation
        if self.suggestion_widget.isVisible():
            if event.key() in (Qt.Key.Key_Up, Qt.Key.Key_Down):
                # Navigate suggestions
                current = self.suggestion_widget.currentRow()
                if event.key() == Qt.Key.Key_Up and current > 0:
                    self.suggestion_widget.setCurrentRow(current - 1)
                elif event.key() == Qt.Key.Key_Down and current < self.suggestion_widget.count() - 1:
                    self.suggestion_widget.setCurrentRow(current + 1)
                event.accept()
                return
            elif event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Tab):
                # Accept suggestion
                suggestion = self.suggestion_widget.get_selected_suggestion()
                if suggestion:
                    self._insert_suggestion(suggestion)
                    self.suggestion_widget.hide()
                event.accept()
                return
            elif event.key() == Qt.Key.Key_Escape:
                # Hide suggestions
                self.suggestion_widget.hide()
                event.accept()
                return
        
        # Process normal key press
        super().keyPressEvent(event)
        
        # Trigger autocomplete for supported languages
        if self.current_language in ["TAU", "TCE", "CNL"]:
            if event.text() and not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                self._trigger_autocomplete()
            elif event.key() == Qt.Key.Key_Space and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # Force trigger with Ctrl+Space
                self._trigger_autocomplete(force=True)
    
    def _trigger_autocomplete(self, force: bool = False):
        """Trigger autocomplete after delay."""
        self.autocomplete_timer.stop()
        delay = 100 if force else 300
        self.autocomplete_timer.start(delay)
    
    def _fetch_suggestions(self):
        """Fetch educational autocomplete suggestions."""
        cursor = self.textCursor()
        
        # Get current word/phrase
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        word = cursor.selectedText()
        
        # Also get last few words for TCE patterns
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(
            QTextCursor.MoveOperation.EndOfLine,
            QTextCursor.MoveMode.KeepAnchor
        )
        line = cursor.selectedText()
        
        # Determine what to search for
        search_text = word
        if self.current_language == "TCE":
            # For TCE, use more context
            words = line.split()
            if len(words) >= 2:
                search_text = " ".join(words[-2:])
        
        if not search_text or len(search_text) < 1:
            self.suggestion_widget.hide()
            return
        
        # Fetch suggestions
        suggestions, context_hint, learning_tip = self.autocomplete_service.fetch_suggestions(
            search_text,
            self.current_language,
            self.learning_level
        )
        
        # Update hints
        self.context_hint = context_hint or ""
        self.learning_tip = learning_tip or ""
        
        # Show status hints
        if context_hint or learning_tip:
            hint = context_hint or learning_tip
            QToolTip.showText(self.mapToGlobal(self.cursorRect().bottomRight()), hint)
        
        # Display suggestions
        if suggestions:
            cursor_rect = self.cursorRect()
            global_pos = self.mapToGlobal(cursor_rect.bottomLeft())
            self.suggestion_widget.show_suggestions(suggestions, global_pos)
        else:
            self.suggestion_widget.hide()
    
    def _insert_suggestion(self, suggestion: EducationalSuggestion):
        """Insert selected suggestion."""
        cursor = self.textCursor()
        
        # Determine insertion mode
        if suggestion.template and "$" in suggestion.template:
            # Use template with placeholders
            self._insert_template(suggestion.template, cursor)
        else:
            # Simple text insertion
            cursor.select(QTextCursor.SelectionType.WordUnderCursor)
            cursor.insertText(suggestion.text)
            self.setTextCursor(cursor)
    
    def _insert_template(self, template: str, cursor: QTextCursor):
        """Insert template with cursor positioning."""
        # Replace word with template
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        
        # Find first placeholder position
        placeholder_pos = template.find('$')
        if placeholder_pos >= 0:
            # Insert text before placeholder
            before = template[:placeholder_pos]
            after = template[placeholder_pos + 1:]
            
            cursor.insertText(before)
            start_pos = cursor.position()
            
            # Insert placeholder or continue
            if after:
                cursor.insertText(after.replace('$', ''))
            
            # Position cursor at placeholder
            cursor.setPosition(start_pos)
            self.setTextCursor(cursor)
        else:
            cursor.insertText(template)
            self.setTextCursor(cursor)
    
    def focusOutEvent(self, event):
        """Hide suggestions when losing focus."""
        super().focusOutEvent(event)
        self.suggestion_widget.hide()


class TauTranslatorEducational(QMainWindow):
    """Tau Translator with Educational AutoComplete."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tau Translator - Educational Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Header with learning controls
        header_layout = QHBoxLayout()
        
        header_layout.addWidget(QLabel("Tau Translator - Educational Edition"))
        header_layout.addStretch()
        
        # Learning level selector
        header_layout.addWidget(QLabel("Learning Level:"))
        self.learning_level = QComboBox()
        self.learning_level.addItems(['Beginner', 'Intermediate', 'Advanced'])
        self.learning_level.setCurrentText('Intermediate')
        self.learning_level.currentTextChanged.connect(self._on_learning_level_changed)
        header_layout.addWidget(self.learning_level)
        
        layout.addLayout(header_layout)
        
        # Control bar
        control_layout = QHBoxLayout()
        
        # Language selectors
        self.left_language = QComboBox()
        self.left_language.addItems(['PLAIN_ENGLISH', 'TAU', 'TCE', 'CNL'])
        self.left_language.currentTextChanged.connect(self._on_left_language_changed)
        
        self.right_language = QComboBox()
        self.right_language.addItems(['TAU', 'PLAIN_ENGLISH', 'TCE', 'CNL'])
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
        
        # Educational hints panel
        hints_group = QGroupBox("Educational Hints")
        hints_layout = QVBoxLayout(hints_group)
        
        self.context_hint_label = QLabel("Context hints will appear here...")
        self.context_hint_label.setWordWrap(True)
        self.context_hint_label.setStyleSheet("color: #0070f3; padding: 5px;")
        hints_layout.addWidget(self.context_hint_label)
        
        self.learning_tip_label = QLabel("Learning tips will appear here...")
        self.learning_tip_label.setWordWrap(True)
        self.learning_tip_label.setStyleSheet("color: #059862; padding: 5px;")
        hints_layout.addWidget(self.learning_tip_label)
        
        layout.addWidget(hints_group)
        
        # Editor panels
        editor_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left editor
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.Box)
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("Input (Ctrl+Space for suggestions)"))
        self.left_editor = CodeEditorWithEducationalAutoComplete()
        self.left_editor.setPlaceholderText("Enter text here... Educational autocomplete enabled for TAU, TCE, and CNL")
        left_layout.addWidget(self.left_editor)
        
        # Right editor
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.Box)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("Output"))
        self.right_editor = CodeEditorWithEducationalAutoComplete()
        self.right_editor.setPlaceholderText("Translation will appear here...")
        right_layout.addWidget(self.right_editor)
        
        editor_splitter.addWidget(left_frame)
        editor_splitter.addWidget(right_frame)
        layout.addWidget(editor_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready. Educational autocomplete enabled.")
        
        # Initialize settings
        self._on_learning_level_changed(self.learning_level.currentText())
        self._on_left_language_changed(self.left_language.currentText())
        self._on_right_language_changed(self.right_language.currentText())
        
        # Update hints periodically
        self.hint_timer = QTimer()
        self.hint_timer.timeout.connect(self._update_hints)
        self.hint_timer.start(1000)  # Update every second
    
    def _on_learning_level_changed(self, level):
        """Handle learning level change."""
        level_map = {
            'Beginner': 'beginner',
            'Intermediate': 'intermediate',
            'Advanced': 'advanced'
        }
        mapped_level = level_map.get(level, 'intermediate')
        self.left_editor.set_learning_level(mapped_level)
        self.right_editor.set_learning_level(mapped_level)
        self.status_bar.showMessage(f"Learning level set to {level}", 2000)
    
    def _on_left_language_changed(self, language):
        """Handle left language change."""
        self.left_editor.set_language(language)
        if language in ["TAU", "TCE", "CNL"]:
            self.status_bar.showMessage(f"Educational autocomplete enabled for {language}", 2000)
    
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
        
        # Use educational translation service
        self.status_bar.showMessage("Translating...", 0)
        
        # TODO: Implement actual translation
        # For now, show placeholder
        result = f"// Educational translation from {self.left_language.currentText()} to {self.right_language.currentText()}\n"
        result += f"// Learning level: {self.learning_level.currentText()}\n\n"
        result += source_text
        
        self.right_editor.setPlainText(result)
        self.status_bar.showMessage("Translation complete", 3000)
    
    def _update_hints(self):
        """Update educational hints display."""
        # Get hints from active editor
        active_editor = self.left_editor if self.left_editor.hasFocus() else self.right_editor
        
        if active_editor.context_hint:
            self.context_hint_label.setText(f"💡 Context: {active_editor.context_hint}")
        
        if active_editor.learning_tip:
            self.learning_tip_label.setText(f"📚 Tip: {active_editor.learning_tip}")


def main():
    """Run the educational application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tau Translator Educational")
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #e0e0e0;
            border-radius: 4px;
            margin-top: 6px;
            padding-top: 6px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """)
    
    window = TauTranslatorEducational()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()