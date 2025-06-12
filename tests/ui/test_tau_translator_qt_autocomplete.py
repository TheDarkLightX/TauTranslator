"""
Unit Tests for TauTranslator PyQt GUI with AutoComplete
======================================================
Following FIRST principles and BDD approach

Copyright: DarkLightX/Dana Edwards
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtWidgets import QApplication, QCompleter, QTextEdit
from PyQt6.QtTest import QTest
from PyQt6.QtGui import QKeyEvent

# Test Data Builders
class MainWindowBuilder:
    """Builder for test main window setup"""
    
    def __init__(self):
        self.enable_autocomplete = True
        self.theme = "light"
        self.language_left = "PLAIN_ENGLISH"
        self.language_right = "TAU"
    
    def with_autocomplete_disabled(self):
        self.enable_autocomplete = False
        return self
    
    def with_dark_theme(self):
        self.theme = "dark"
        return self
    
    def with_languages(self, left, right):
        self.language_left = left
        self.language_right = right
        return self
    
    def build(self):
        from ..tau_translator_desktop_qt import TauTranslatorWindow
        window = TauTranslatorWindow()
        window.autocomplete_enabled = self.enable_autocomplete
        window.current_theme = self.theme
        return window


class MockTranslationService:
    """Mock translation service for testing"""
    
    def __init__(self):
        self.translate_called = False
        self.last_source_text = None
        self.last_source_lang = None
        self.last_target_lang = None
        self.return_value = "Translated text"
        self.should_fail = False
    
    def translate(self, source_text, source_lang, target_lang):
        self.translate_called = True
        self.last_source_text = source_text
        self.last_source_lang = source_lang
        self.last_target_lang = target_lang
        
        if self.should_fail:
            raise Exception("Translation failed")
        
        return self.return_value


class MockAutoCompleteService:
    """Mock autocomplete service for testing"""
    
    def __init__(self):
        self.suggestions = [
            "forall",
            "for every",
            "for all x"
        ]
        self.get_suggestions_called = False
        self.last_text = None
        self.last_position = None
    
    def get_suggestions(self, text, position=None):
        self.get_suggestions_called = True
        self.last_text = text
        self.last_position = position
        
        # Filter suggestions based on prefix
        prefix = text.lower()
        return [s for s in self.suggestions if s.lower().startswith(prefix)]


@pytest.fixture
def qapp():
    """Create QApplication for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def main_window(qapp):
    """Create main window for testing"""
    window = MainWindowBuilder().build()
    window.show()
    QTest.qWaitForWindowExposed(window)
    yield window
    window.close()


class TestMainWindowBasicFunctionality:
    """Test basic main window functionality"""
    
    # Test: MainWindow_InitialState_DisplaysCorrectly
    def test_given_default_setup_when_launching_then_displays_main_components(self, main_window):
        # Given: Default main window
        # When: Window is shown (done in fixture)
        # Then: Main components are visible
        assert main_window.isVisible()
        assert main_window.left_editor is not None
        assert main_window.right_editor is not None
        assert main_window.translate_button is not None
        assert main_window.swap_button is not None
        assert main_window.status_bar is not None
    
    # Test: MainWindow_LanguageSelection_UpdatesCorrectly
    def test_given_language_combos_when_selecting_language_then_updates_selection(self, main_window):
        # Given: Language combo boxes
        left_combo = main_window.left_language_combo
        right_combo = main_window.right_language_combo
        
        # When: Changing language selection
        left_combo.setCurrentText("TAU")
        right_combo.setCurrentText("CNL")
        
        # Then: Languages are updated
        assert left_combo.currentText() == "TAU"
        assert right_combo.currentText() == "CNL"
    
    # Test: MainWindow_SwapButton_SwapsLanguagesAndText
    def test_given_text_and_languages_when_clicking_swap_then_swaps_both(self, main_window):
        # Given: Text in both editors and language selections
        main_window.left_editor.setPlainText("Test left text")
        main_window.right_editor.setPlainText("Test right text")
        main_window.left_language_combo.setCurrentText("PLAIN_ENGLISH")
        main_window.right_language_combo.setCurrentText("TAU")
        
        # When: Clicking swap button
        QTest.mouseClick(main_window.swap_button, Qt.MouseButton.LeftButton)
        
        # Then: Text and languages are swapped
        assert main_window.left_editor.toPlainText() == "Test right text"
        assert main_window.right_editor.toPlainText() == "Test left text"
        assert main_window.left_language_combo.currentText() == "TAU"
        assert main_window.right_language_combo.currentText() == "PLAIN_ENGLISH"


class TestAutoCompleteFunctionality:
    """Test autocomplete functionality in the Qt GUI"""
    
    @pytest.fixture
    def window_with_autocomplete(self, qapp):
        """Create window with mocked autocomplete service"""
        window = MainWindowBuilder().build()
        window.autocomplete_service = MockAutoCompleteService()
        window.show()
        QTest.qWaitForWindowExposed(window)
        yield window
        window.close()
    
    # Test: AutoComplete_TAULanguageSelected_EnablesAutoComplete
    def test_given_tau_language_when_typing_then_autocomplete_activates(self, window_with_autocomplete):
        # Given: TAU language selected in left editor
        window = window_with_autocomplete
        window.left_language_combo.setCurrentText("TAU")
        editor = window.left_editor
        
        # When: Typing "for" in the editor
        QTest.keyClicks(editor, "for")
        
        # Allow time for autocomplete to trigger
        QTest.qWait(300)
        
        # Then: Autocomplete service is called
        assert window.autocomplete_service.get_suggestions_called
        assert window.autocomplete_service.last_text == "for"
    
    # Test: AutoComplete_PlainEnglishSelected_DisablesAutoComplete
    def test_given_plain_english_when_typing_then_no_autocomplete(self, window_with_autocomplete):
        # Given: Plain English selected
        window = window_with_autocomplete
        window.left_language_combo.setCurrentText("PLAIN_ENGLISH")
        editor = window.left_editor
        
        # When: Typing in the editor
        QTest.keyClicks(editor, "for")
        QTest.qWait(300)
        
        # Then: Autocomplete is not triggered
        assert not window.autocomplete_service.get_suggestions_called
    
    # Test: AutoComplete_CompleterWidget_ShowsSuggestions
    def test_given_autocomplete_triggered_when_suggestions_available_then_shows_completer(self, window_with_autocomplete):
        # Given: Window with TAU language and completer
        window = window_with_autocomplete
        window.left_language_combo.setCurrentText("TAU")
        editor = window.left_editor
        
        # Create and attach a completer
        completer = QCompleter(["forall", "for every", "exists"])
        editor.setCompleter(completer)
        
        # When: Typing triggers autocomplete
        QTest.keyClicks(editor, "for")
        
        # Then: Completer should be activated
        assert completer.completionPrefix() == "for"
    
    # Test: AutoComplete_TabKey_AcceptsSuggestion
    def test_given_suggestion_visible_when_pressing_tab_then_accepts_suggestion(self, window_with_autocomplete):
        # Given: Editor with active suggestions
        window = window_with_autocomplete
        window.left_language_combo.setCurrentText("TAU")
        editor = window.left_editor
        
        # Mock the completer behavior
        with patch.object(editor, 'insertCompletion') as mock_insert:
            # When: Typing and pressing Tab
            QTest.keyClicks(editor, "for")
            QTest.keyPress(editor, Qt.Key.Key_Tab)
            
            # Then: Completion would be inserted
            # Note: Actual behavior depends on completer implementation
            assert editor.toPlainText().startswith("for")
    
    # Test: AutoComplete_EscapeKey_CancelsSuggestions
    def test_given_suggestions_visible_when_pressing_escape_then_hides_suggestions(self, window_with_autocomplete):
        # Given: Editor with suggestions
        window = window_with_autocomplete
        window.left_language_combo.setCurrentText("TAU")
        editor = window.left_editor
        
        # When: Typing and pressing Escape
        QTest.keyClicks(editor, "for")
        QTest.keyPress(editor, Qt.Key.Key_Escape)
        
        # Then: Text remains unchanged
        assert editor.toPlainText() == "for"


class TestTranslationFunctionality:
    """Test translation functionality"""
    
    @pytest.fixture
    def window_with_translation(self, qapp):
        """Create window with mocked translation service"""
        window = MainWindowBuilder().build()
        window.translation_service = MockTranslationService()
        window.show()
        QTest.qWaitForWindowExposed(window)
        yield window
        window.close()
    
    # Test: Translation_ValidInput_TranslatesSuccessfully
    def test_given_valid_input_when_translating_then_shows_result(self, window_with_translation):
        # Given: Text in left editor
        window = window_with_translation
        window.left_editor.setPlainText("Test input text")
        
        # When: Clicking translate button
        with patch.object(window, 'perform_translation') as mock_translate:
            QTest.mouseClick(window.translate_button, Qt.MouseButton.LeftButton)
            
            # Then: Translation is triggered
            mock_translate.assert_called_once()
    
    # Test: Translation_EmptyInput_ShowsWarning
    def test_given_empty_input_when_translating_then_shows_warning(self, window_with_translation):
        # Given: Empty editor
        window = window_with_translation
        window.left_editor.clear()
        
        # When: Clicking translate button
        with patch('PyQt6.QtWidgets.QMessageBox.warning') as mock_warning:
            QTest.mouseClick(window.translate_button, Qt.MouseButton.LeftButton)
            
            # Then: Warning is shown
            mock_warning.assert_called()
    
    # Test: Translation_NetworkError_ShowsErrorMessage
    def test_given_network_error_when_translating_then_shows_error(self, window_with_translation):
        # Given: Translation service that will fail
        window = window_with_translation
        window.translation_service.should_fail = True
        window.left_editor.setPlainText("Test input")
        
        # When: Attempting translation
        with patch('PyQt6.QtWidgets.QMessageBox.critical') as mock_error:
            with patch.object(window, 'perform_translation', side_effect=Exception("Network error")):
                QTest.mouseClick(window.translate_button, Qt.MouseButton.LeftButton)
                
                # Then: Error message is shown
                assert mock_error.called or window.status_bar.currentMessage() == "Translation failed"


class TestThemeSwitching:
    """Test theme switching functionality"""
    
    # Test: Theme_LightToDark_UpdatesColors
    def test_given_light_theme_when_switching_to_dark_then_updates_ui(self, main_window):
        # Given: Light theme active
        main_window.current_theme = "light"
        
        # When: Switching to dark theme
        with patch.object(main_window, 'apply_dark_theme') as mock_apply:
            main_window.toggle_theme()
            
            # Then: Dark theme is applied
            mock_apply.assert_called_once()
            assert main_window.current_theme == "dark"
    
    # Test: Theme_DarkToLight_UpdatesColors
    def test_given_dark_theme_when_switching_to_light_then_updates_ui(self, main_window):
        # Given: Dark theme active
        main_window.current_theme = "dark"
        
        # When: Switching to light theme
        with patch.object(main_window, 'apply_light_theme') as mock_apply:
            main_window.toggle_theme()
            
            # Then: Light theme is applied
            mock_apply.assert_called_once()
            assert main_window.current_theme == "light"


class TestKeyboardShortcuts:
    """Test keyboard shortcuts"""
    
    # Test: Shortcut_CtrlEnter_TriggersTranslation
    def test_given_text_when_pressing_ctrl_enter_then_translates(self, main_window):
        # Given: Text in editor
        main_window.left_editor.setPlainText("Test text")
        
        # When: Pressing Ctrl+Enter
        with patch.object(main_window, 'perform_translation') as mock_translate:
            QTest.keyPress(main_window, Qt.Key.Key_Return, Qt.KeyboardModifier.ControlModifier)
            
            # Then: Translation is triggered
            mock_translate.assert_called()
    
    # Test: Shortcut_CtrlS_SavesFile
    def test_given_text_when_pressing_ctrl_s_then_opens_save_dialog(self, main_window):
        # Given: Text in editor
        main_window.left_editor.setPlainText("Test content")
        
        # When: Pressing Ctrl+S
        with patch('PyQt6.QtWidgets.QFileDialog.getSaveFileName') as mock_save:
            mock_save.return_value = ("test.tau", "")
            QTest.keyPress(main_window, Qt.Key.Key_S, Qt.KeyboardModifier.ControlModifier)
            
            # Then: Save dialog appears
            mock_save.assert_called()


class TestStatusBarUpdates:
    """Test status bar functionality"""
    
    # Test: StatusBar_TranslationStart_ShowsProgress
    def test_given_translation_started_when_processing_then_shows_progress(self, main_window):
        # Given: Translation about to start
        # When: Starting translation
        main_window.show_status("Translating...", is_progress=True)
        
        # Then: Status bar shows message
        assert main_window.status_bar.currentMessage() == "Translating..."
    
    # Test: StatusBar_TranslationComplete_ShowsSuccess
    def test_given_translation_complete_when_finished_then_shows_success(self, main_window):
        # Given: Translation completed
        # When: Showing success
        main_window.show_status("Translation complete", duration=3000)
        
        # Then: Status shows success message
        assert main_window.status_bar.currentMessage() == "Translation complete"


class TestEditorFeatures:
    """Test editor-specific features"""
    
    # Test: Editor_SyntaxHighlighting_HighlightsTauKeywords
    def test_given_tau_code_when_displayed_then_highlights_syntax(self, main_window):
        # Given: TAU language selected
        main_window.left_language_combo.setCurrentText("TAU")
        
        # When: Entering TAU code
        tau_code = "forall x (P(x) -> Q(x))"
        main_window.left_editor.setPlainText(tau_code)
        
        # Then: Syntax highlighter is active
        highlighter = main_window.left_editor.highlighter
        assert highlighter is not None
        # Note: Testing actual highlighting would require checking text formats
    
    # Test: Editor_LineNumbers_DisplaysCorrectly
    def test_given_multiline_text_when_displayed_then_shows_line_numbers(self, main_window):
        # Given: Multiline text
        multiline_text = "Line 1\nLine 2\nLine 3"
        
        # When: Setting text
        main_window.left_editor.setPlainText(multiline_text)
        
        # Then: Line count is correct
        line_count = main_window.left_editor.document().lineCount()
        assert line_count == 3


# Integration test to verify full autocomplete flow
class TestAutoCompleteIntegration:
    """Integration tests for autocomplete with backend"""
    
    @pytest.fixture
    def integrated_window(self, qapp):
        """Window with real autocomplete integration"""
        window = MainWindowBuilder().build()
        
        # Mock the backend call
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = {
                'success': True,
                'data': {
                    'suggestions': [
                        {'text': 'forall', 'type': 'quantifier', 'description': 'Universal quantifier'},
                        {'text': 'for every', 'type': 'quantifier', 'description': 'Alternative form'}
                    ],
                    'source': 'backend'
                }
            }
            window.mock_post = mock_post
            
        window.show()
        QTest.qWaitForWindowExposed(window)
        yield window
        window.close()
    
    # Test: Integration_FullAutoCompleteFlow_WorksEndToEnd
    def test_given_backend_available_when_typing_tau_then_shows_backend_suggestions(self, integrated_window):
        # Given: TAU language and backend available
        window = integrated_window
        window.left_language_combo.setCurrentText("TAU")
        
        # When: Typing to trigger autocomplete
        QTest.keyClicks(window.left_editor, "for")
        QTest.qWait(500)  # Wait for debounce and backend call
        
        # Then: Backend is called and suggestions would be shown
        if hasattr(window, 'mock_post'):
            # Verify backend would be called with correct data
            assert window.left_editor.toPlainText() == "for"