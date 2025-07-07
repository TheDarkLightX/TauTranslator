#!/usr/bin/env python3
"""
TauTranslatorOmega - Professional PyQt6 Interface
================================================

A modern, professional desktop application using PyQt6 that matches
and exceeds the PWA design with native Qt capabilities.

Features:
- Native look and feel on all platforms
- Professional code editor with syntax highlighting
- Dark/Light theme support
- Tabbed interface
- Dock widgets for flexible layout
- Status bar with progress indicators
- Modern Material-inspired design

Author: DarkLightX/Dana Edwards
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import threading
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QComboBox, QSplitter, QFrame,
    QDockWidget, QTreeWidget, QTreeWidgetItem, QTabWidget,
    QToolBar, QStatusBar, QMenuBar, QMenu, QGroupBox,
    QGridLayout, QProgressBar, QMessageBox, QFileDialog,
    QStyle, QStyleFactory, QSizePolicy
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QSettings, QSize, QPropertyAnimation,
    QEasingCurve, pyqtProperty, QPoint, QMetaObject, Q_ARG
)
from PyQt6.QtGui import (
    QAction, QFont, QFontDatabase, QColor, QPalette, QIcon,
    QTextCharFormat, QSyntaxHighlighter, QTextDocument, QPixmap,
    QPainter, QPainterPath, QLinearGradient
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
# Add project root to path for backend imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import translation engine components
from backend.unified.translators.bidirectional_engine import BidirectionalTranslationEngine
from backend.unified.translators.base import TranslationDirection


class TauSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Tau language."""
    
    def __init__(self, document):
        super().__init__(document)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0070f3"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'always', 'sometimes', 'never', 'eventually', 'until',
            'forall', 'exists', 'sbf', 'ifile', 'ofile', 'console',
            'true', 'false', 'and', 'or', 'not', 'implies'
        ]
        for word in keywords:
            self.highlighting_rules.append((f'\\b{word}\\b', keyword_format))
        
        # Operators
        operator_format = QTextCharFormat()
        operator_format.setForeground(QColor("#d73a49"))
        operator_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((':=|->|<->|&&|\\|\\||!|=|!=|<|>|<=|>=', operator_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#005cc5"))
        self.highlighting_rules.append(('\\b[0-9]+\\b', number_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#032f62"))
        self.highlighting_rules.append(('"[^"]*"', string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6a737d"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append(('//[^\n]*', comment_format))
        self.highlighting_rules.append(('#[^\n]*', comment_format))
        
        # Function definitions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#6f42c1"))
        function_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append(('\\b\\w+(?=\\s*\\()', function_format))
        
    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        for pattern, format in self.highlighting_rules:
            import re
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)


class CodeEditor(QTextEdit):
    """Enhanced code editor with line numbers and syntax highlighting."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set monospace font
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)
        
        # Enable syntax highlighting
        self.highlighter = TauSyntaxHighlighter(self.document())
        
        # Set tab width
        self.setTabStopDistance(40)
        
        # Style
        self.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #0070f3;
                selection-color: white;
            }
        """)


class TranslationWorker(QThread):
    """Worker thread for translation operations."""
    
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, translator, source_text, source_format, target_format):
        super().__init__()
        self.translator = translator
        self.source_text = source_text
        self.source_format = source_format
        self.target_format = target_format
        
    def run(self):
        """Perform translation in background thread."""
        try:
            self.progress.emit("Starting translation...")
            
            # Map UI format names to TranslationDirection enum
            direction_map = {
                ('Natural Language', 'Tau Language'): TranslationDirection.NL_TO_TAU,
                ('Natural Language', 'TCE'): TranslationDirection.NL_TO_TCE,
                ('Tau Language', 'TCE'): TranslationDirection.TO_TCE,  # Tau->TCE for viewing
                ('Tau Language', 'Natural Language'): TranslationDirection.TO_ENGLISH,
                ('Tau Language', 'ILR'): TranslationDirection.TO_TCE,  # Tau->ILR via TCE
                ('TCE', 'Tau Language'): TranslationDirection.TCE_TO_TAU,
                ('TCE', 'Natural Language'): TranslationDirection.TCE_TO_NL,
                ('TCE', 'ILR'): TranslationDirection.TO_TCE,  # TCE->ILR
                ('ILR', 'Tau Language'): TranslationDirection.TO_TAU,
                ('ILR', 'Natural Language'): TranslationDirection.TO_ENGLISH,
                ('ILR', 'TCE'): TranslationDirection.TO_TCE  # ILR->TCE
            }
            
            direction_key = (self.source_format, self.target_format)
            if direction_key not in direction_map:
                self.error.emit(f"Translation from {self.source_format} to {self.target_format} is not currently supported.")
                return
            
            direction = direction_map[direction_key]
            
            # Perform translation using unified interface
            import time
            result = self.translator.translate(self.source_text, direction, start_time=time.time())
            
            # Check if result has success attribute (TranslationResult)
            # or if it's a Result monad that needs unwrapping
            if hasattr(result, 'success'):
                # Direct TranslationResult object
                if result.success:
                    self.finished.emit({
                        'success': True,
                        'output': result.translated_text,
                        'confidence': result.confidence,
                        'patterns': result.metadata.get('patterns', []) if result.metadata else []
                    })
                else:
                    self.error.emit(f"Translation failed: {result.error_message or 'Unknown error'}")
            else:
                # Assume it's a Result monad - try to unwrap it
                if hasattr(result, 'unwrap'):
                    try:
                        unwrapped = result.unwrap()
                        self.finished.emit({
                            'success': True,
                            'output': unwrapped.translated_text,
                            'confidence': unwrapped.confidence,
                            'patterns': unwrapped.metadata.get('patterns', []) if unwrapped.metadata else []
                        })
                    except Exception as e:
                        self.error.emit(f"Translation failed: {str(e)}")
                else:
                    self.error.emit(f"Translation failed: unexpected result type")
                
        except Exception as e:
            self.error.emit(f"Translation error: {str(e)}")


class TauTranslatorQt(QMainWindow):
    """Main application window using PyQt6."""
    
    def __init__(self):
        super().__init__()
        
        # Application state
        self.translator = None
        self.current_theme = "light"
        self.translation_count = 0
        self.session_start = datetime.now()
        
        # Settings
        self.settings = QSettings('TauTranslator', 'TauTranslatorOmega')
        
        # Setup UI
        self.init_ui()
        self.load_translator()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Tau Translator Alpha")
        self.setGeometry(100, 100, 1600, 900)
        
        # Set application style
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
        # Central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        # Create UI components
        self.create_menu_bar()
        self.create_tool_bar()
        self.create_central_widget()
        self.create_dock_widgets()
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction('&Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('&Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('&Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        edit_menu.addAction(redo_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        theme_action = QAction('Toggle &Theme', self)
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        validate_action = QAction('&Validate Grammar', self)
        validate_action.setShortcut('F5')
        tools_menu.addAction(validate_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_tool_bar(self):
        """Create the main toolbar."""
        toolbar = QToolBar('Main Toolbar')
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.addToolBar(toolbar)
        
        # Translation formats
        self.source_combo = QComboBox()
        self.source_combo.addItems(['Natural Language', 'Tau Language', 'TCE', 'ILR'])
        self.source_combo.setMinimumWidth(150)
        toolbar.addWidget(QLabel(' From: '))
        toolbar.addWidget(self.source_combo)
        
        toolbar.addSeparator()
        
        self.target_combo = QComboBox()
        self.target_combo.addItems(['Tau Language', 'TCE', 'ILR', 'Natural Language'])
        self.target_combo.setMinimumWidth(150)
        toolbar.addWidget(QLabel(' To: '))
        toolbar.addWidget(self.target_combo)
        
        toolbar.addSeparator()
        
        # Translate button
        self.translate_btn = QPushButton('Translate')
        self.translate_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.translate_btn.clicked.connect(self.translate)
        toolbar.addWidget(self.translate_btn)
        
        # Add spacer
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Theme toggle
        self.theme_btn = QPushButton('🌙')
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #e0e0e0;
                border-radius: 20px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        toolbar.addWidget(self.theme_btn)
        
    def create_central_widget(self):
        """Create the central editor area."""
        central_widget = self.centralWidget()
        layout = QVBoxLayout(central_widget)
        
        # Create splitter for input/output
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Input editor
        input_group = QGroupBox("Input")
        input_layout = QVBoxLayout(input_group)
        self.input_editor = CodeEditor()
        self.input_editor.setPlaceholderText("Enter text to translate...")
        input_layout.addWidget(self.input_editor)
        
        # Output editor
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        self.output_editor = CodeEditor()
        self.output_editor.setPlaceholderText("Translation will appear here...")
        self.output_editor.setReadOnly(True)
        output_layout.addWidget(self.output_editor)
        
        splitter.addWidget(input_group)
        splitter.addWidget(output_group)
        splitter.setSizes([800, 800])
        
        layout.addWidget(splitter)
        
    def create_dock_widgets(self):
        """Create dockable side panels."""
        # Project explorer dock
        project_dock = QDockWidget("Project Explorer", self)
        project_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                   Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabel("Files")
        
        # Add sample items
        root = QTreeWidgetItem(self.project_tree, ["TauProject"])
        QTreeWidgetItem(root, ["main.tau"])
        QTreeWidgetItem(root, ["rules.tce"])
        QTreeWidgetItem(root, ["config.json"])
        root.setExpanded(True)
        
        project_dock.setWidget(self.project_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, project_dock)
        
        # Properties dock
        properties_dock = QDockWidget("Properties", self)
        properties_dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        
        # Create tab widget for properties
        self.properties_tabs = QTabWidget()
        
        # Grammar tab
        grammar_widget = QWidget(self.properties_tabs)
        grammar_layout = QVBoxLayout(grammar_widget)
        self.grammar_status = QLabel("No grammar loaded")
        self.grammar_details = QTextEdit()
        self.grammar_details.setReadOnly(True)
        self.grammar_details.setMaximumHeight(200)
        grammar_layout.addWidget(self.grammar_status)
        grammar_layout.addWidget(self.grammar_details)
        
        # LLM Status section
        llm_group = QGroupBox("LLM Status")
        llm_layout = QVBoxLayout()
        self.llm_status = QLabel("Checking LLM...")
        self.llm_details = QTextEdit()
        self.llm_details.setReadOnly(True)
        self.llm_details.setMaximumHeight(150)
        llm_layout.addWidget(self.llm_status)
        llm_layout.addWidget(self.llm_details)
        llm_group.setLayout(llm_layout)
        
        grammar_layout.addWidget(llm_group)
        grammar_layout.addStretch()
        self.properties_tabs.addTab(grammar_widget, "Grammar & LLM")
        
        # History tab
        history_widget = QWidget(self.properties_tabs)
        history_layout = QVBoxLayout(history_widget)
        
        # Translation history
        history_label = QLabel("Translation History:")
        history_layout.addWidget(history_label)
        self.history_list = QTreeWidget(history_widget)
        self.history_list.setHeaderLabels(["Time", "From", "To", "Status"])
        self.history_list.setMaximumHeight(200)
        history_layout.addWidget(self.history_list)
        
        # Conversation context display
        context_label = QLabel("LLM Conversation Context:")
        history_layout.addWidget(context_label)
        self.conversation_context = QTextEdit()
        self.conversation_context.setReadOnly(True)
        self.conversation_context.setPlaceholderText("Conversation history will appear here...")
        history_layout.addWidget(self.conversation_context)
        
        # Clear history button
        clear_btn = QPushButton("Clear Conversation History")
        clear_btn.clicked.connect(self.clear_conversation_history)
        history_layout.addWidget(clear_btn)
        
        self.properties_tabs.addTab(history_widget, "History")
        
        # Validation tab
        validation_widget = QWidget(self.properties_tabs)
        validation_layout = QVBoxLayout(validation_widget)
        self.validation_output = QTextEdit(validation_widget)
        self.validation_output.setReadOnly(True)
        validation_layout.addWidget(self.validation_output)
        self.properties_tabs.addTab(validation_widget, "Validation")
        
        properties_dock.setWidget(self.properties_tabs)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, properties_dock)
        
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Status message
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.progress_bar)
        
        # Permanent widgets
        self.translation_count_label = QLabel("Translations: 0")
        self.status_bar.addPermanentWidget(self.translation_count_label)
        
        self.session_time_label = QLabel("Session: 0m")
        self.status_bar.addPermanentWidget(self.session_time_label)
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_session_time)
        self.timer.start(60000)  # Update every minute
        
    def apply_theme(self):
        """Apply the current theme to the application."""
        if self.current_theme == "dark":
            # Dark theme
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
            dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
            QApplication.setPalette(dark_palette)
            
            # Update editor styles
            editor_style = """
                QTextEdit {
                    background-color: #2d2d2d;
                    border: 1px solid #555;
                    color: #f0f0f0;
                }
            """
            self.input_editor.setStyleSheet(editor_style)
            self.output_editor.setStyleSheet(editor_style)
            
            self.theme_btn.setText("☀️")
        else:
            # Light theme (default)
            QApplication.setPalette(QApplication.style().standardPalette())
            
            # Update editor styles
            editor_style = """
                QTextEdit {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    color: #333333;
                }
            """
            self.input_editor.setStyleSheet(editor_style)
            self.output_editor.setStyleSheet(editor_style)
            
            self.theme_btn.setText("🌙")
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.settings.setValue('theme', self.current_theme)
        
    def load_translator(self):
        """Load the translator in a background thread."""
        def load():
            try:
                self.translator = BidirectionalTranslationEngine()
                # Thread-safe UI update - check if widget still exists
                try:
                    QMetaObject.invokeMethod(self.status_label, "setText", 
                        Qt.ConnectionType.QueuedConnection, 
                        Q_ARG(str, "Translator loaded successfully"))
                    # Update grammar and LLM status
                    QMetaObject.invokeMethod(self, "update_grammar_llm_status", 
                        Qt.ConnectionType.QueuedConnection)
                except RuntimeError:
                    pass  # Widget was deleted
            except Exception as e:
                # Thread-safe UI update - check if widget still exists
                try:
                    QMetaObject.invokeMethod(self.status_label, "setText", 
                        Qt.ConnectionType.QueuedConnection, 
                        Q_ARG(str, f"Failed to load translator: {str(e)}"))
                except RuntimeError:
                    pass  # Widget was deleted
                
        thread = threading.Thread(target=load, daemon=True)
        thread.start()
        
    def update_grammar_llm_status(self):
        """Update grammar and LLM status displays (≤10 lines)."""
        if not self.translator:
            return
            
        # Update grammar status
        grammar_info = self.translator.get_grammar_info()
        if grammar_info['available']:
            self.grammar_status.setText(f"Grammar loaded: {grammar_info['preferred']}")
            details = []
            for g in grammar_info['available']:
                details.append(f"• {g['name']}: {g['size']} bytes")
            self.grammar_details.setPlainText("Available grammars:\n" + "\n".join(details))
        else:
            self.grammar_status.setText("No grammar files found")
            self.grammar_details.setPlainText("Missing expected grammar files")
            
        # Update LLM status
        llm_status = self.translator.get_llm_status()
        if llm_status['llm_available']:
            self.llm_status.setText(f"LLM Active: {llm_status['llm_provider']}")
            details = [
                f"Provider: {llm_status['llm_provider'] or 'None'}",
                f"Knowledge Base: {'Enabled' if llm_status['knowledge_base_enabled'] else 'Disabled'}",
                f"Grammar Loaded: {'Yes' if llm_status['grammar_loaded_for_llm'] else 'No'}",
                f"Conversation Tracking: {'Active' if llm_status['conversation_tracking'] else 'Inactive'}",
                f"History Size: {llm_status['conversation_history_size']} translations"
            ]
            self.llm_details.setPlainText("\n".join(details))
        else:
            self.llm_status.setText("LLM Service Not Available")
            self.llm_details.setPlainText("Configure API key for LLM support")
        
    def translate(self):
        """Perform translation."""
        source_text = self.input_editor.toPlainText().strip()
        
        if not source_text:
            QMessageBox.warning(self, "Input Required", "Please enter text to translate")
            return
            
        if not self.translator:
            QMessageBox.error(self, "Translator Not Ready", "Translator is not loaded yet")
            return
            
        # Disable UI during translation
        self.translate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        # Clean up previous worker if exists
        if hasattr(self, 'worker'):
            try:
                if self.worker.isRunning():
                    self.worker.quit()
                    self.worker.wait()
            except RuntimeError:
                # Worker was already deleted
                pass
        
        # Create worker thread
        self.worker = TranslationWorker(
            self.translator,
            source_text,
            self.source_combo.currentText(),
            self.target_combo.currentText()
        )
        
        # Connect signals
        self.worker.finished.connect(self.on_translation_finished)
        self.worker.progress.connect(self.on_translation_progress)
        self.worker.error.connect(self.on_translation_error)
        self.worker.finished.connect(lambda: self.worker.deleteLater())
        
        # Start translation
        self.worker.start()
        
    def on_translation_finished(self, result):
        """Handle translation completion."""
        try:
            self.output_editor.setPlainText(result.get('output', ''))
            
            # Update statistics
            self.translation_count += 1
            self.translation_count_label.setText(f"Translations: {self.translation_count}")
            
            # Add to history
            time_str = datetime.now().strftime("%H:%M:%S")
            item = QTreeWidgetItem([
                time_str,
                self.source_combo.currentText(),
                self.target_combo.currentText(),
                "Success"
            ])
            self.history_list.insertTopLevelItem(0, item)
            
            # Update validation tab
            confidence = result.get('confidence', 0)
            patterns = result.get('patterns', [])
            validation_text = f"Translation successful\n"
            validation_text += f"Confidence: {confidence:.1%}\n"
            validation_text += f"Patterns detected: {', '.join(patterns) if patterns else 'None'}"
            self.validation_output.setPlainText(validation_text)
            
            # Update conversation context display
            self.update_conversation_display()
            
            # Update LLM status to show conversation history size
            self.update_grammar_llm_status()
            
            self.status_label.setText("Translation complete")
        except Exception as e:
            QMessageBox.error(self, "Display Error", f"Failed to display results: {str(e)}")
        finally:
            # Re-enable UI
            self.translate_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
        
    def on_translation_progress(self, message):
        """Handle translation progress updates."""
        self.status_label.setText(message)
        
    def on_translation_error(self, error):
        """Handle translation errors."""
        QMessageBox.critical(self, "Translation Error", error)
        
        # Re-enable UI
        self.translate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Translation failed")
        
        # Add to history
        time_str = datetime.now().strftime("%H:%M:%S")
        item = QTreeWidgetItem([
            time_str,
            self.source_combo.currentText(),
            self.target_combo.currentText(),
            "Failed"
        ])
        self.history_list.insertTopLevelItem(0, item)
        
    def update_session_time(self):
        """Update session time display."""
        elapsed = datetime.now() - self.session_start
        minutes = int(elapsed.total_seconds() / 60)
        self.session_time_label.setText(f"Session: {minutes}m")
        
    def update_conversation_display(self):
        """Update the conversation context display (≤10 lines)."""
        if not self.translator:
            return
            
        # Get conversation summary
        summary = self.translator.get_conversation_summary()
        
        if summary['total_translations'] == 0:
            self.conversation_context.setPlainText("No translations yet in this session.")
            return
            
        # Build conversation display
        lines = [f"Total translations: {summary['total_translations']}"]
        lines.append(f"Average confidence: {summary['average_confidence']:.1%}")
        lines.append("\nRecent translations:")
        
        # Show last 5 from conversation history
        if hasattr(self.translator, 'conversation_history'):
            for entry in self.translator.conversation_history[-5:]:
                lines.append(f"\n[{entry['timestamp'].split('T')[1][:8]}]")
                lines.append(f"Input: {entry['input']}")
                lines.append(f"Output: {entry['output']}")
                if 'explanation' in entry:
                    lines.append(f"Explanation: {entry['explanation']}")
                    
        self.conversation_context.setPlainText("\n".join(lines))
        
    def clear_conversation_history(self):
        """Clear the conversation history (≤10 lines)."""
        if not self.translator:
            return
            
        reply = QMessageBox.question(
            self, 'Clear History',
            'Clear conversation history? This will reset the LLM context.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.translator.clear_conversation_history()
            self.conversation_context.clear()
            self.update_grammar_llm_status()
            self.status_label.setText("Conversation history cleared")
        
    def new_file(self):
        """Create a new file."""
        self.input_editor.clear()
        self.output_editor.clear()
        self.status_label.setText("New file created")
        
    def open_file(self):
        """Open a file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Tau Files (*.tau);;TCE Files (*.tce);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_editor.setPlainText(content)
                self.status_label.setText(f"Opened: {Path(filename).name}")
            except Exception as e:
                QMessageBox.error(self, "Error", f"Failed to open file: {str(e)}")
                
    def save_file(self):
        """Save the current file."""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save File", "",
            "Tau Files (*.tau);;TCE Files (*.tce);;All Files (*.*)"
        )
        
        if filename:
            try:
                content = self.output_editor.toPlainText()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.setText(f"Saved: {Path(filename).name}")
            except Exception as e:
                QMessageBox.error(self, "Error", f"Failed to save file: {str(e)}")
                
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About TauTranslator",
            "<h2>Tau Translator Alpha</h2>"
            "<p>Version 3.0.0</p>"
            "<p>A professional tool for translating between Tau language "
            "and natural language specifications.</p>"
            "<p>Built with PyQt6 for superior performance and native feel.</p>"
            "<p>© 2024 TauTranslator Team</p>"
        )
        
    def closeEvent(self, event):
        """Handle application close event."""
        # Stop timer
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        # Clean up worker thread
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
        
        # Save settings
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('windowState', self.saveState())
        
        # Confirm exit if there's unsaved content
        if self.input_editor.toPlainText().strip():
            reply = QMessageBox.question(
                self, 'Confirm Exit',
                'You have unsaved changes. Do you want to exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
                
        event.accept()


def main():
    """Launch the PyQt6 application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("TauTranslator")
    app.setOrganizationName("TauTranslator")
    app.setApplicationDisplayName("Tau Translator Alpha")
    
    # Load custom fonts if available (QFontDatabase is static in PyQt6)
    
    # Create and show main window
    window = TauTranslatorQt()
    
    # Restore window geometry
    settings = QSettings('TauTranslator', 'TauTranslatorOmega')
    geometry = settings.value('geometry')
    if geometry:
        window.restoreGeometry(geometry)
    state = settings.value('windowState')
    if state:
        window.restoreState(state)
    
    window.show()
    
    # Add sample content
    sample_tau = """// Example Tau Language Code
sbf input_stream = ifile("sensor_data.txt")
sbf output_stream = ofile("alerts.log")

// Define monitoring rules
r temperature_check[t] = temperature[t] > 80
r pressure_check[t] = pressure[t] < 100

// Safety constraints
always (temperature_check[t] -> trigger_alarm[t])
sometimes (pressure_check[t] && temperature_check[t])

// Functions
alert_level(t, p) := (t > 90) ? "critical" : "warning"
"""
    
    window.input_editor.setPlainText(sample_tau)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()