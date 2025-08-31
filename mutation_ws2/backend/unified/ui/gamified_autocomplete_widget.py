"""
Main gamified autocomplete widget for TauTranslator.

Integrates educational autocomplete with gamification UI.
Production-ready with animations and error handling.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Dict
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget,
    QListWidgetItem, QSplitter, QPushButton, QLabel, QFrame,
    QApplication, QMainWindow, QMessageBox, QToolBar, QStatusBar
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect,
    QEasingCurve, QParallelAnimationGroup, QSequentialAnimationGroup
)
from PyQt6.QtGui import QFont, QIcon, QAction, QKeySequence

from ..core.gamified_autocomplete_app import GamifiedAutocompleteApplication
from ..core.autocomplete.models import (
    SuggestionRequest, SpecificationContext, LanguageMode,
    ContextType, DifficultyLevel, CursorPosition
)
from ..infrastructure.gamification_ui import (
    GamificationDashboard, AnimatedProgressBar
)
from ..domain.gamification_types import Achievement, ExperiencePoints

class AutocompleteSuggestionItem(QListWidgetItem):
    """Custom list item for autocomplete suggestions."""
    
    def __init__(self, suggestion):
        """Initialize with suggestion data."""
        super().__init__()
        self.suggestion = suggestion
        
        # Format display text
        display = f"{suggestion.display} - {suggestion.category.value}"
        self.setText(display)
        
        # Set tooltip with description and example
        tooltip = f"{suggestion.description}\n\nExample:\n{suggestion.example}"
        self.setToolTip(tooltip)
        
        # Style based on difficulty
        self._apply_difficulty_styling()
    
    def _apply_difficulty_styling(self):
        """Apply visual styling based on difficulty."""
        colors = {
            "beginner": "#4CAF50",
            "intermediate": "#FF9800",
            "advanced": "#F44336"
        }
        
        color = colors.get(self.suggestion.difficulty.value, "#000000")
        self.setForeground(Qt.GlobalColor.black)
        self.setBackground(Qt.GlobalColor.white)

class GamifiedAutocompleteWidget(QWidget):
    """
    Main widget combining code editor with gamified autocomplete.
    
    Features:
    - Real-time autocomplete suggestions
    - XP animations on suggestion use
    - Achievement notifications
    - Integrated gamification dashboard
    """
    
    translation_requested = pyqtSignal(str, str, str)  # text, from_lang, to_lang
    
    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize the gamified autocomplete widget."""
        super().__init__(parent)
        
        # Initialize application layer
        self._app = GamifiedAutocompleteApplication()
        self._current_language = LanguageMode.TAU
        
        # UI components
        self._editor: Optional[QTextEdit] = None
        self._suggestions_list: Optional[QListWidget] = None
        self._dashboard: Optional[GamificationDashboard] = None
        self._xp_animation_label: Optional[QLabel] = None
        
        # Autocomplete state
        self._autocomplete_timer = QTimer()
        self._autocomplete_timer.timeout.connect(self._update_suggestions)
        self._autocomplete_timer.setSingleShot(True)
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
        # Load initial data
        self._load_initial_state()
    
    def _setup_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Editor and suggestions
        editor_widget = self._create_editor_widget()
        splitter.addWidget(editor_widget)
        
        # Right side: Gamification dashboard
        self._dashboard = self._app.get_dashboard_widget()
        splitter.addWidget(self._dashboard)
        
        # Set initial splitter sizes (70/30 split)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        
        # Create floating XP animation label
        self._create_xp_animation_label()
        
        # Status bar at bottom
        self._status_label = QLabel("Ready")
        self._status_label.setStyleSheet("padding: 5px;")
        main_layout.addWidget(self._status_label)
    
    def _create_editor_widget(self) -> QWidget:
        """Create the editor and suggestions widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Language selector
        lang_bar = QHBoxLayout()
        lang_label = QLabel("Language:")
        lang_bar.addWidget(lang_label)
        
        tau_btn = QPushButton("TAU")
        tau_btn.setCheckable(True)
        tau_btn.setChecked(True)
        tau_btn.clicked.connect(lambda: self._set_language(LanguageMode.TAU))
        lang_bar.addWidget(tau_btn)
        
        tce_btn = QPushButton("TCE")
        tce_btn.setCheckable(True)
        tce_btn.clicked.connect(lambda: self._set_language(LanguageMode.TCE))
        lang_bar.addWidget(tce_btn)
        
        lang_bar.addStretch()
        layout.addLayout(lang_bar)
        
        # Editor
        self._editor = QTextEdit()
        self._editor.setFont(QFont("Consolas", 12))
        self._editor.setPlaceholderText(
            "Start typing to see suggestions...\n\n"
            "Try: 'forall', 'solve', 'always', or natural language patterns"
        )
        layout.addWidget(self._editor, 3)
        
        # Suggestions list
        suggestions_label = QLabel("Suggestions:")
        suggestions_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(suggestions_label)
        
        self._suggestions_list = QListWidget()
        self._suggestions_list.setMaximumHeight(200)
        layout.addWidget(self._suggestions_list, 1)
        
        return widget
    
    def _create_xp_animation_label(self):
        """Create floating label for XP animations."""
        self._xp_animation_label = QLabel(self)
        self._xp_animation_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: white;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self._xp_animation_label.hide()
    
    def _connect_signals(self):
        """Connect widget signals."""
        # Editor signals
        self._editor.textChanged.connect(self._on_text_changed)
        self._editor.cursorPositionChanged.connect(self._on_cursor_changed)
        
        # Suggestion selection
        self._suggestions_list.itemDoubleClicked.connect(self._use_suggestion)
        
        # Gamification signals
        self._app.xp_gained.connect(self._animate_xp_gain)
        self._app.achievement_unlocked.connect(self._show_achievement)
        self._app.level_up.connect(self._show_level_up)
    
    def _load_initial_state(self):
        """Load initial challenges and profile state."""
        # Get daily challenges
        challenges = self._app.get_daily_challenges()
        
        # Update status
        profile = self._app._profile
        if profile:
            self._update_status(
                f"Welcome back! Level {profile.current_level} | "
                f"{profile.total_xp} XP | 🔥 {profile.daily_streak} day streak"
            )
    
    def _on_text_changed(self):
        """Handle text changes in editor."""
        # Reset autocomplete timer
        self._autocomplete_timer.stop()
        self._autocomplete_timer.start(300)  # 300ms delay
    
    def _on_cursor_changed(self):
        """Handle cursor position changes."""
        # Could update context-sensitive help here
        pass
    
    def _update_suggestions(self):
        """Update autocomplete suggestions."""
        # Get current context
        context = self._build_context()
        
        # Create request
        request = SuggestionRequest(
            context=context,
            max_suggestions=10,
            include_templates=True,
            include_examples=True
        )
        
        # Get suggestions
        result = self._app.process_autocomplete_request(request)
        
        if result.is_success():
            self._display_suggestions(result.value)
        else:
            self._suggestions_list.clear()
    
    def _build_context(self) -> SpecificationContext:
        """Build context from current editor state."""
        text = self._editor.toPlainText()
        cursor_pos = self._editor.textCursor().position()
        
        # Determine context type from text
        context_type = self._detect_context_type(text, cursor_pos)
        
        return SpecificationContext(
            full_text=text,
            cursor_position=CursorPosition(cursor_pos),
            language_mode=self._current_language,
            context_type=context_type,
            parent_constructs=[],  # Would parse for real context
            variables_in_scope=[],  # Would extract from parsed AST
            learning_level=DifficultyLevel.INTERMEDIATE
        )
    
    def _detect_context_type(self, text: str, cursor_pos: int) -> ContextType:
        """Detect context type from text around cursor."""
        # Get text before cursor
        before_cursor = text[:cursor_pos].lower()
        
        # Simple pattern matching
        if "solve" in before_cursor[-20:]:
            return ContextType.SOLVER_COMMAND
        elif any(kw in before_cursor[-20:] for kw in ["always", "eventually", "sometimes"]):
            return ContextType.TEMPORAL_CONSTRAINT
        elif any(kw in before_cursor[-20:] for kw in ["forall", "exists"]):
            return ContextType.QUANTIFIER_EXPRESSION
        elif "define" in before_cursor[-20:]:
            return ContextType.FUNCTION_DEFINITION
        else:
            return ContextType.LOGICAL_ASSERTION
    
    def _display_suggestions(self, response):
        """Display suggestions in list widget."""
        self._suggestions_list.clear()
        
        for suggestion in response.suggestions:
            item = AutocompleteSuggestionItem(suggestion)
            self._suggestions_list.addItem(item)
        
        # Update status with learning tip
        if response.learning_tip:
            self._update_status(f"💡 {response.learning_tip}")
    
    def _use_suggestion(self, item: AutocompleteSuggestionItem):
        """Use selected suggestion."""
        suggestion = item.suggestion
        
        # Insert suggestion text at cursor
        cursor = self._editor.textCursor()
        cursor.insertText(suggestion.text)
        
        # Track usage for gamification
        context = self._build_context()
        self._app.use_suggestion(suggestion, context)
        
        # Clear suggestions
        self._suggestions_list.clear()
    
    def _set_language(self, language: LanguageMode):
        """Set current language mode."""
        self._current_language = language
        self._update_suggestions()
        self._update_status(f"Switched to {language.value} mode")
    
    def _animate_xp_gain(self, xp: int):
        """Animate XP gain notification."""
        self._xp_animation_label.setText(f"+{xp} XP")
        
        # Position near editor
        editor_rect = self._editor.geometry()
        x = editor_rect.center().x() - 50
        y = editor_rect.center().y()
        
        self._xp_animation_label.move(x, y)
        self._xp_animation_label.show()
        
        # Create animation sequence
        self._xp_animation_label.setGeometry(x, y, 100, 40)
        
        # Fade and move up animation
        anim_group = QParallelAnimationGroup()
        
        # Position animation
        pos_anim = QPropertyAnimation(self._xp_animation_label, b"geometry")
        pos_anim.setDuration(1000)
        pos_anim.setStartValue(QRect(x, y, 100, 40))
        pos_anim.setEndValue(QRect(x, y - 50, 100, 40))
        pos_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        anim_group.addAnimation(pos_anim)
        
        # Opacity animation
        opacity_anim = QPropertyAnimation(self._xp_animation_label, b"windowOpacity")
        opacity_anim.setDuration(1000)
        opacity_anim.setStartValue(1.0)
        opacity_anim.setEndValue(0.0)
        anim_group.addAnimation(opacity_anim)
        
        # Hide after animation
        anim_group.finished.connect(self._xp_animation_label.hide)
        anim_group.start()
    
    def _show_achievement(self, achievement: Achievement):
        """Show achievement unlock notification."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Achievement Unlocked!")
        msg.setText(f"🏆 {achievement.name}")
        msg.setInformativeText(
            f"{achievement.description}\n\n"
            f"+{achievement.points} XP"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.show()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, msg.close)
    
    def _show_level_up(self, level: int):
        """Show level up notification."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Level Up!")
        msg.setText(f"🎉 Congratulations! You've reached Level {level}!")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.show()
        
        # Auto-close after 3 seconds
        QTimer.singleShot(3000, msg.close)
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self._status_label.setText(message)
        
        # Auto-clear after 5 seconds
        QTimer.singleShot(5000, lambda: self._status_label.setText("Ready"))
    
    def save_progress(self):
        """Save current progress."""
        result = self._app.save_progress()
        if result.is_success():
            self._update_status("Progress saved ✓")
        else:
            self._update_status(f"Save failed: {result.error}")
    
    def translate_selection(self):
        """Translate selected text between TAU and TCE."""
        cursor = self._editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            
            # Determine translation direction
            from_lang = self._current_language
            to_lang = LanguageMode.TCE if from_lang == LanguageMode.TAU else LanguageMode.TAU
            
            # Request translation
            result = self._app._autocomplete_service.translate_selection_async(
                text, from_lang, to_lang
            )
            
            if result.is_success():
                # Replace selection with translation
                cursor.insertText(result.value)
                
                # Track translation for gamification
                self._app.complete_translation(text, result.value, from_lang.value, to_lang.value)
            else:
                self._update_status(f"Translation failed: {result.error}")

class GamifiedAutocompleteWindow(QMainWindow):
    """Main window for standalone gamified autocomplete."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        self.setWindowTitle("TauTranslator - Gamified Learning")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        self._autocomplete = GamifiedAutocompleteWidget()
        self.setCentralWidget(self._autocomplete)
        
        # Create menus and toolbar
        self._create_menus()
        self._create_toolbar()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_menus(self):
        """Create application menus."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Progress", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._autocomplete.save_progress)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        translate_action = QAction("Translate Selection", self)
        translate_action.setShortcut("Ctrl+T")
        translate_action.triggered.connect(self._autocomplete.translate_selection)
        edit_menu.addAction(translate_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        dashboard_action = QAction("Toggle Dashboard", self)
        dashboard_action.setShortcut("Ctrl+D")
        dashboard_action.setCheckable(True)
        dashboard_action.setChecked(True)
        view_menu.addAction(dashboard_action)
    
    def _create_toolbar(self):
        """Create application toolbar."""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Save button
        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self._autocomplete.save_progress)
        toolbar.addWidget(save_btn)
        
        toolbar.addSeparator()
        
        # Translate button
        translate_btn = QPushButton("🔄 Translate")
        translate_btn.clicked.connect(self._autocomplete.translate_selection)
        toolbar.addWidget(translate_btn)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save progress before closing
        self._autocomplete.save_progress()
        event.accept()

# Example usage
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show window
    window = GamifiedAutocompleteWindow()
    window.show()
    
    sys.exit(app.exec())