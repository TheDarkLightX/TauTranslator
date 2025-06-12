#!/usr/bin/env python3
"""
TauTranslator Complete Gamified Educational Application

Production-ready application combining:
- Educational autocomplete with TAU/TCE support
- Gamification system with achievements and challenges
- Clean architecture following Intentional Disclosure Principle
- Polished UI with animations and visual feedback

Copyright: DarkLightX/Dana Edwards
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

# Add backend to path
backend_path = Path(__file__).parent.parent / 'backend' / 'unified'
sys.path.insert(0, str(backend_path))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QComboBox, QSplitter, QFrame,
    QStatusBar, QMenuBar, QMenu, QMessageBox, QToolBar, QStyle
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QThread, QSettings, QSize, QPropertyAnimation,
    QEasingCurve, QRect, pyqtProperty, QPoint
)
from PyQt6.QtGui import (
    QAction, QFont, QFontDatabase, QIcon, QKeySequence,
    QTextCharFormat, QTextCursor, QColor, QPalette
)

# Import backend components
from domain.gamification_types import (
    UserId, KeywordCategory, EducationalContext,
    GamificationConfig, SkillArea
)
from domain.gamification_service import GamificationDomainService
from infrastructure.gamification_persistence import SQLiteGamificationRepository
from infrastructure.gamification_ui import (
    GamificationDashboard, NotificationManager,
    SkillProgressWidget, AchievementUnlockDialog
)
from core.gamified_autocomplete_app import GamifiedAutocompleteApplication
from core.gamification_error_handler import ErrorHandlingDecorator
from core.autocomplete import (
    EducationalAutocompleteService,
    AutocompleteConfiguration,
    SuggestionRequest,
    SpecificationContext,
    LanguageMode,
    DifficultyLevel,
    ContextType,
    CursorPosition
)

# Import syntax highlighter
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
try:
    from tau_translator_desktop_qt import TauSyntaxHighlighter
except:
    TauSyntaxHighlighter = None


class TranslationWorker(QThread):
    """Worker thread for translations."""
    
    translation_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, source_text: str, source_lang: str, target_lang: str):
        super().__init__()
        self.source_text = source_text
        self.source_lang = source_lang
        self.target_lang = target_lang
    
    def run(self):
        """Perform translation in background."""
        try:
            # Mock translation for demo
            # In production, call actual translation service
            import time
            time.sleep(0.5)  # Simulate processing
            
            result = f"// Translated from {self.source_lang} to {self.target_lang}\n"
            result += f"// Original: {self.source_text[:50]}...\n\n"
            
            if self.target_lang == "TAU":
                # Simple mock translations
                if "for all" in self.source_text.lower():
                    result += "forall x : condition(x)"
                elif "always" in self.source_text.lower():
                    result += "always (property)"
                else:
                    result += "// TAU translation here"
            else:
                result += self.source_text
            
            self.translation_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class GamifiedCodeEditor(QTextEdit):
    """Enhanced code editor with gamification integration."""
    
    suggestion_selected = pyqtSignal(str, str)  # text, category
    translation_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_editor()
        
        # Autocomplete state
        self.current_language = LanguageMode.TAU
        self.learning_level = DifficultyLevel.INTERMEDIATE
        self.highlighter = None
        
        # Autocomplete service
        self.autocomplete_service = EducationalAutocompleteService()
        self.suggestion_timer = QTimer()
        self.suggestion_timer.timeout.connect(self._fetch_suggestions)
        self.suggestion_timer.setSingleShot(True)
        
        # Current suggestions
        self.current_suggestions = []
        self.suggestion_popup = None
    
    def _setup_editor(self):
        """Configure editor appearance."""
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        
        # Enable syntax highlighting for TAU
        if TauSyntaxHighlighter:
            self.highlighter = TauSyntaxHighlighter(self.document())
    
    def set_language_mode(self, mode: str):
        """Set language mode for autocomplete."""
        mode_map = {
            'TAU': LanguageMode.TAU,
            'TCE': LanguageMode.TCE,
            'PLAIN_ENGLISH': LanguageMode.TAU  # Default to TAU
        }
        self.current_language = mode_map.get(mode, LanguageMode.TAU)
    
    def set_learning_level(self, level: str):
        """Set learning level."""
        level_map = {
            'beginner': DifficultyLevel.BEGINNER,
            'intermediate': DifficultyLevel.INTERMEDIATE,
            'advanced': DifficultyLevel.ADVANCED
        }
        self.learning_level = level_map.get(level.lower(), DifficultyLevel.INTERMEDIATE)
    
    def keyPressEvent(self, event):
        """Handle key events for autocomplete."""
        # Handle Enter key for translation
        if event.key() == Qt.Key.Key_Return and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.translation_requested.emit()
            return
        
        # Normal key processing
        super().keyPressEvent(event)
        
        # Trigger autocomplete
        if event.text() and not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.suggestion_timer.stop()
            self.suggestion_timer.start(300)  # 300ms debounce
    
    def _fetch_suggestions(self):
        """Fetch autocomplete suggestions."""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.WordUnderCursor)
        current_word = cursor.selectedText()
        
        if not current_word:
            return
        
        # Create context
        context = SpecificationContext(
            full_text=self.toPlainText(),
            cursor_position=CursorPosition(cursor.position()),
            language_mode=self.current_language,
            context_type=self._infer_context_type(current_word),
            learning_level=self.learning_level
        )
        
        # Create request
        request = SuggestionRequest(
            context=context,
            max_suggestions=5,
            include_templates=True,
            include_examples=True
        )
        
        # Get suggestions
        result = self.autocomplete_service.get_suggestions_async(request)
        
        if result.is_success():
            response = result.value
            self.current_suggestions = response.suggestions
            
            # Show suggestions (simplified for demo)
            if self.current_suggestions:
                self._show_suggestions_popup(cursor)
    
    def _infer_context_type(self, word: str) -> ContextType:
        """Infer context type from current word."""
        word_lower = word.lower()
        
        if word_lower in ['always', 'sometimes', 'eventually', 'never']:
            return ContextType.TEMPORAL_CONSTRAINT
        elif word_lower in ['forall', 'exists']:
            return ContextType.QUANTIFIER_EXPRESSION
        elif word_lower == 'solve':
            return ContextType.SOLVER_COMMAND
        else:
            return ContextType.LOGICAL_ASSERTION
    
    def _show_suggestions_popup(self, cursor):
        """Show suggestions in tooltip (simplified)."""
        if not self.current_suggestions:
            return
        
        # Create suggestion text
        suggestion_text = "\n".join([
            f"{i+1}. {s.text} - {s.description}"
            for i, s in enumerate(self.current_suggestions[:3])
        ])
        
        # Show as tooltip
        from PyQt6.QtWidgets import QToolTip
        cursor_rect = self.cursorRect(cursor)
        global_pos = self.mapToGlobal(cursor_rect.bottomLeft())
        QToolTip.showText(global_pos, suggestion_text, self)
        
        # Auto-complete first suggestion on Tab
        if self.current_suggestions:
            first = self.current_suggestions[0]
            # Emit signal for gamification
            self.suggestion_selected.emit(first.text, first.category.value)


class TauTranslatorGamifiedComplete(QMainWindow):
    """Complete gamified Tau Translator application."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tau Translator - Educational Gamified Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize gamification
        self._init_gamification()
        
        # Setup UI
        self._setup_ui()
        
        # Setup menus
        self._setup_menus()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # Save every 30 seconds
        
        # Check daily login
        self._check_daily_login()
    
    def _init_gamification(self):
        """Initialize gamification system."""
        # Create repository
        db_path = Path.home() / '.tau_translator' / 'gamification.db'
        db_path.parent.mkdir(exist_ok=True)
        
        repository = SQLiteGamificationRepository(str(db_path))
        
        # Create domain service
        config = GamificationConfig()
        domain_service = GamificationDomainService(config)
        
        # Create error handler
        error_handler = ErrorHandlingDecorator(
            logger_name="TauTranslator.Gamification"
        )
        
        # Create application service
        self.gamification_app = GamifiedAutocompleteApplication(
            repository=repository,
            domain_service=domain_service,
            error_handler=error_handler,
            user_id=UserId("default_user")
        )
        
        # Initialize or load progress
        self.gamification_app.initialize_user_progress()
        
        # Create notification manager
        self.notification_manager = NotificationManager(self)
    
    def _setup_ui(self):
        """Setup main UI components."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        
        # Gamification dashboard
        self.dashboard = GamificationDashboard(self.gamification_app, self)
        main_layout.addWidget(self.dashboard)
        
        # Control bar
        control_layout = QHBoxLayout()
        
        # Language selectors
        control_layout.addWidget(QLabel("From:"))
        self.source_language = QComboBox()
        self.source_language.addItems(['PLAIN_ENGLISH', 'TAU', 'TCE'])
        self.source_language.currentTextChanged.connect(self._on_source_language_changed)
        control_layout.addWidget(self.source_language)
        
        control_layout.addWidget(QLabel("To:"))
        self.target_language = QComboBox()
        self.target_language.addItems(['TAU', 'PLAIN_ENGLISH', 'TCE'])
        control_layout.addWidget(self.target_language)
        
        control_layout.addStretch()
        
        # Translate button
        self.translate_button = QPushButton("Translate (Ctrl+Enter)")
        self.translate_button.clicked.connect(self._perform_translation)
        self.translate_button.setStyleSheet("""
            QPushButton {
                background-color: #0070f3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051cc;
            }
        """)
        control_layout.addWidget(self.translate_button)
        
        main_layout.addLayout(control_layout)
        
        # Editor splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Source editor
        source_frame = QFrame()
        source_frame.setFrameStyle(QFrame.Shape.Box)
        source_layout = QVBoxLayout(source_frame)
        source_layout.addWidget(QLabel("Source Text"))
        
        self.source_editor = GamifiedCodeEditor()
        self.source_editor.suggestion_selected.connect(self._on_suggestion_selected)
        self.source_editor.translation_requested.connect(self._perform_translation)
        self.source_editor.setPlaceholderText(
            "Start typing to see educational autocomplete suggestions!\n"
            "Try: always, forall, solve, if...then\n"
            "Press Ctrl+Enter to translate"
        )
        source_layout.addWidget(self.source_editor)
        
        # Target editor
        target_frame = QFrame()
        target_frame.setFrameStyle(QFrame.Shape.Box)
        target_layout = QVBoxLayout(target_frame)
        target_layout.addWidget(QLabel("Translation Result"))
        
        self.target_editor = GamifiedCodeEditor()
        self.target_editor.setReadOnly(True)
        target_layout.addWidget(self.target_editor)
        
        splitter.addWidget(source_frame)
        splitter.addWidget(target_frame)
        splitter.setSizes([700, 700])
        
        main_layout.addWidget(splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_bar()
        
        # Translation worker
        self.translation_worker = None
    
    def _setup_menus(self):
        """Setup application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_document)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        achievements_action = QAction("Achievements", self)
        achievements_action.setShortcut("Ctrl+Shift+A")
        achievements_action.triggered.connect(self.dashboard.show_achievements)
        view_menu.addAction(achievements_action)
        
        challenges_action = QAction("Daily Challenges", self)
        challenges_action.setShortcut("Ctrl+Shift+C")
        challenges_action.triggered.connect(self.dashboard.show_challenges)
        view_menu.addAction(challenges_action)
        
        skills_action = QAction("Skill Progress", self)
        skills_action.setShortcut("Ctrl+Shift+S")
        skills_action.triggered.connect(self._show_skills)
        view_menu.addAction(skills_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        tutorial_action = QAction("Tutorial", self)
        tutorial_action.triggered.connect(self._show_tutorial)
        help_menu.addAction(tutorial_action)
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _check_daily_login(self):
        """Check daily login for streak."""
        try:
            notifications = self.gamification_app.check_daily_login()
            
            for notification in notifications:
                self.notification_manager.show_notification(
                    notification.message,
                    notification.notification_type,
                    notification.icon
                )
            
            # Update dashboard
            self.dashboard.refresh()
            
        except Exception as e:
            print(f"Daily login check failed: {e}")
    
    def _on_source_language_changed(self, language: str):
        """Handle source language change."""
        self.source_editor.set_language_mode(language)
        self._update_status_bar()
    
    def _on_suggestion_selected(self, text: str, category: str):
        """Handle autocomplete suggestion selection."""
        try:
            # Map to keyword category
            category_map = {
                'temporal': KeywordCategory.TEMPORAL,
                'quantifier': KeywordCategory.QUANTIFIER,
                'operator': KeywordCategory.OPERATOR,
                'solver': KeywordCategory.SOLVER,
                'keyword': KeywordCategory.KEYWORD
            }
            keyword_category = category_map.get(category, KeywordCategory.KEYWORD)
            
            # Create context
            context = EducationalContext(
                language_mode=self.source_language.currentText(),
                learning_level=self.dashboard.get_current_difficulty(),
                session_start=datetime.now()
            )
            
            # Record keyword use
            notifications = self.gamification_app.record_keyword_use(
                keyword=text,
                category=keyword_category,
                context=context
            )
            
            # Show notifications
            for notification in notifications:
                self.notification_manager.show_notification(
                    notification.message,
                    notification.notification_type,
                    notification.icon
                )
            
            # Update dashboard
            self.dashboard.refresh()
            
            # Check for achievement unlocks
            self._check_achievement_unlocks(notifications)
            
        except Exception as e:
            print(f"Failed to record keyword use: {e}")
    
    def _perform_translation(self):
        """Perform translation with gamification."""
        source_text = self.source_editor.toPlainText().strip()
        
        if not source_text:
            self.status_bar.showMessage("Enter text to translate", 3000)
            return
        
        # Disable button during translation
        self.translate_button.setEnabled(False)
        self.status_bar.showMessage("Translating...")
        
        # Create worker thread
        self.translation_worker = TranslationWorker(
            source_text,
            self.source_language.currentText(),
            self.target_language.currentText()
        )
        
        self.translation_worker.translation_complete.connect(self._on_translation_complete)
        self.translation_worker.error_occurred.connect(self._on_translation_error)
        self.translation_worker.start()
    
    def _on_translation_complete(self, result: str):
        """Handle translation completion."""
        # Show result
        self.target_editor.setPlainText(result)
        
        # Record translation for gamification
        try:
            is_perfect = len(result.strip()) > 0 and "error" not in result.lower()
            
            notifications = self.gamification_app.record_translation(
                source_language=self.source_language.currentText(),
                target_language=self.target_language.currentText(),
                source_length=len(self.source_editor.toPlainText()),
                is_perfect=is_perfect
            )
            
            # Show notifications
            for notification in notifications:
                self.notification_manager.show_notification(
                    notification.message,
                    notification.notification_type,
                    notification.icon
                )
            
            # Update dashboard
            self.dashboard.refresh()
            
        except Exception as e:
            print(f"Failed to record translation: {e}")
        
        # Re-enable button
        self.translate_button.setEnabled(True)
        self.status_bar.showMessage("Translation complete!", 3000)
    
    def _on_translation_error(self, error: str):
        """Handle translation error."""
        QMessageBox.warning(self, "Translation Error", f"Translation failed: {error}")
        self.translate_button.setEnabled(True)
        self.status_bar.showMessage("Translation failed", 3000)
    
    def _check_achievement_unlocks(self, notifications: List[Any]):
        """Check for achievement unlocks in notifications."""
        for notification in notifications:
            if notification.notification_type == 'achievement_unlock':
                # Show achievement dialog
                try:
                    achievement = self.gamification_app.get_achievement_details(
                        notification.data.get('achievement_id')
                    )
                    if achievement:
                        dialog = AchievementUnlockDialog(achievement, self)
                        dialog.show()
                except:
                    pass
    
    def _update_status_bar(self):
        """Update status bar with current state."""
        lang_mode = self.source_language.currentText()
        if lang_mode in ['TAU', 'TCE']:
            self.status_bar.showMessage(
                f"Educational autocomplete active for {lang_mode}. "
                "Start typing to earn XP!"
            )
        else:
            self.status_bar.showMessage("Ready")
    
    def _auto_save(self):
        """Auto-save gamification progress."""
        try:
            self.gamification_app.save_progress()
        except Exception as e:
            print(f"Auto-save failed: {e}")
    
    def _new_document(self):
        """Create new document."""
        reply = QMessageBox.question(
            self,
            "New Document",
            "Clear current content?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.source_editor.clear()
            self.target_editor.clear()
    
    def _show_skills(self):
        """Show skill progress dialog."""
        try:
            skills = self.gamification_app.get_user_skills()
            widget = SkillProgressWidget(skills, self)
            widget.show()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load skills: {e}")
    
    def _show_tutorial(self):
        """Show tutorial."""
        tutorial_text = """
        <h2>Welcome to Tau Translator - Educational Gamified Edition!</h2>
        
        <h3>Getting Started:</h3>
        <ul>
        <li>Type TAU keywords to see autocomplete suggestions</li>
        <li>Each suggestion used earns you XP</li>
        <li>Complete translations for bonus XP</li>
        <li>Maintain daily streaks for multipliers</li>
        </ul>
        
        <h3>Gamification Features:</h3>
        <ul>
        <li><b>XP System:</b> Earn experience for every action</li>
        <li><b>Levels:</b> Progress through 10 levels</li>
        <li><b>Achievements:</b> Unlock badges for milestones</li>
        <li><b>Daily Challenges:</b> Complete tasks for bonus rewards</li>
        <li><b>Skill Tracking:</b> Monitor your progress in 7 areas</li>
        </ul>
        
        <h3>Tips:</h3>
        <ul>
        <li>Try temporal operators: always, sometimes, eventually</li>
        <li>Use quantifiers: forall, exists</li>
        <li>Explore solver commands: solve x = 0</li>
        <li>Press Ctrl+Enter to translate quickly</li>
        </ul>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Tutorial")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(tutorial_text)
        msg.exec()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
        <h2>Tau Translator - Educational Gamified Edition</h2>
        <p>Version 1.0.0</p>
        
        <p>An educational tool for learning formal specification languages
        through gamification and intelligent autocomplete.</p>
        
        <p><b>Features:</b></p>
        <ul>
        <li>TAU and TCE language support</li>
        <li>Educational autocomplete with examples</li>
        <li>Gamification system for engagement</li>
        <li>Progress tracking and achievements</li>
        </ul>
        
        <p>Copyright: DarkLightX/Dana Edwards</p>
        """
        
        QMessageBox.about(self, "About Tau Translator", about_text)
    
    def closeEvent(self, event):
        """Save on close."""
        try:
            self.gamification_app.save_progress()
        except:
            pass
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tau Translator Gamified")
    app.setOrganizationName("DarkLightX")
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8fafc;
        }
        QFrame {
            background-color: white;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 8px;
        }
        QTextEdit {
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px;
            background-color: #ffffff;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        QComboBox {
            padding: 6px 12px;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            background-color: white;
        }
        QComboBox:hover {
            border-color: #cbd5e1;
        }
        QStatusBar {
            background-color: #f1f5f9;
            border-top: 1px solid #e2e8f0;
        }
    """)
    
    # Create and show main window
    window = TauTranslatorGamifiedComplete()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()