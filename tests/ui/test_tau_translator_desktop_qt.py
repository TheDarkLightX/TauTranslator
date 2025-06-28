import sys
import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtTest import QTest

# Ensure the application source is on the path
SRC_PATH = Path(__file__).parent.parent.parent
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ui.tau_translator_desktop_qt import TauTranslatorQt

@pytest.fixture
def qapp():
    """Create a QApplication instance for the tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

@pytest.fixture
def window(qapp):
    """Create an instance of the main window for testing."""
    # Mock the translator loading to prevent actual backend calls
    with patch.object(TauTranslatorQt, 'load_translator', return_value=None) as mock_load:
        win = TauTranslatorQt()
        win.translator = Mock()
        win.translator.is_available = True
        win.show()
        QTest.qWaitForWindowExposed(win)
        yield win
        win.close()

class TestTauTranslatorQt:
    def test_window_initialization(self, window):
        """Given the app starts, when the window is created, then it should be visible."""
        assert window.isVisible()
        assert window.windowTitle() == "Tau Translator Alpha"

    def test_single_sentence_translation(self, window):
        """Given a single sentence, when translate is clicked, then it produces a single output."""
        # Arrange
        input_text = "a test sentence"
        window.input_editor.setPlainText(input_text)
        window.translator.translate.return_value = {
            'success': True, 
            'translated_text': 'translated sentence',
            'duration': 0.1
        }

        # Act
        QTest.mouseClick(window.translate_button, Qt.MouseButton.LeftButton)
        QTest.qWait(500) # Wait for worker thread to finish

        # Assert
        assert "translated sentence" in window.output_editor.toPlainText()
        window.translator.translate.assert_called_once_with(input_text, 'TCE', 'TAU')

    def test_multi_sentence_translation(self, window):
        """Given multiple sentences, when translate is clicked, then it translates each one sequentially."""
        # Arrange
        input_lines = ["first sentence", "second sentence"]
        input_text = "\n".join(input_lines)
        window.input_editor.setPlainText(input_text)

        # Mock the translation results for each sentence
        window.translator.translate.side_effect = [
            {'success': True, 'translated_text': 'translated first', 'duration': 0.1},
            {'success': True, 'translated_text': 'translated second', 'duration': 0.1}
        ]

        # Act
        QTest.mouseClick(window.translate_button, Qt.MouseButton.LeftButton)
        QTest.qWait(1000) # Wait for both translations

        # Assert
        final_text = window.output_editor.toPlainText()
        assert "translated first" in final_text
        assert "translated second" in final_text
        assert final_text.count('\n') >= 1

        # Verify translator was called for each line
        assert window.translator.translate.call_count == 2
        window.translator.translate.assert_any_call(input_lines[0], 'TCE', 'TAU')
        window.translator.translate.assert_any_call(input_lines[1], 'TCE', 'TAU')
