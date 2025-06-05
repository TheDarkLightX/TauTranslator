import sys
import sys
from pathlib import Path

# Add the project src directory to the path to allow sibling imports
project_src_path = str(Path(__file__).parent.parent.parent)
if project_src_path not in sys.path:
    sys.path.insert(0, project_src_path)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QLabel, QTextEdit, QComboBox, QPushButton, QFormLayout, 
    QSizePolicy
)

from ..lmql_engine.bidirectional_translator import (
    LMQLBidirectionalTranslator,
    TranslationDirection,
    TranslationResult
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tau Translator Omega - Desktop")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Create Translation Tab
        self.translation_tab = QWidget()
        self.tabs.addTab(self.translation_tab, "Translation")
        self.translation_layout = QVBoxLayout(self.translation_tab)
        # --- Translation Tab UI Elements ---

        # Input Type Selector
        self.input_type_combo = QComboBox()
        self.input_type_combo.addItems(["English", "Tau Controlled English (TCE)", "Tau Language", "Intermediate Logic (IL)"])
        
        # Input Text Area
        self.input_text_edit = QTextEdit()
        self.input_text_edit.setPlaceholderText("Enter text to translate...")

        # Output Type Selector
        self.output_type_combo = QComboBox()
        self.output_type_combo.addItems(["Tau Language", "Tau Controlled English (TCE)", "English", "Intermediate Logic (IL)"])

        # Translate Button
        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.handle_translation)

        # Output Text Area
        self.output_text_edit = QTextEdit()
        self.output_text_edit.setPlaceholderText("Translation will appear here...")
        # self.output_text_edit.setReadOnly(True) # Made editable as per user request

        # Layout for Translation Tab
        form_layout = QFormLayout()
        form_layout.addRow(QLabel("Input Type:"), self.input_type_combo)
        form_layout.addRow(QLabel("Output Type:"), self.output_type_combo)

        self.translation_layout.addLayout(form_layout)
        self.translation_layout.addWidget(QLabel("Input:"))
        self.translation_layout.addWidget(self.input_text_edit)
        self.translation_layout.addWidget(self.translate_button)
        self.translation_layout.addWidget(QLabel("Output:"))
        self.translation_layout.addWidget(self.output_text_edit)

        # Set stretch factors for text edits to take available space
        self.translation_layout.setStretchFactor(self.input_text_edit, 1)
        self.translation_layout.setStretchFactor(self.output_text_edit, 1)

        # Initialize the translator
        try:
            self.translator = LMQLBidirectionalTranslator()
            print(f"LMQL Translator Initialized. LMQL Available: {self.translator.use_lmql}")
        except Exception as e:
            self.translator = None
            print(f"Error initializing LMQLBidirectionalTranslator: {e}")
            # Optionally, disable translation button or show error in UI
            self.input_text_edit.setText(f"Error initializing translator: {e}")

    def handle_translation(self):
        if not self.translator:
            self.output_text_edit.setText("Translator not initialized. Check console for errors.")
            return

        input_text = self.input_text_edit.toPlainText().strip()
        # For now, we'll base direction on combo boxes, assuming input_text is the source
        # TODO: A more sophisticated way to determine actual source and target based on focus or dedicated buttons
        
        input_type_str = self.input_type_combo.currentText()
        output_type_str = self.output_type_combo.currentText()

        if not input_text:
            self.output_text_edit.setText("Please enter text to translate.")
            return

        result = None
        # This logic needs to be more robust based on actual types supported by LMQLBidirectionalTranslator
        # Currently it supports Tau <-> TCE
        try:
            if "Tau Language" in input_type_str and "Tau Controlled English (TCE)" in output_type_str:
                print(f"Translating Tau to TCE: {input_text[:50]}...")
                result = self.translator.translate_tau_to_tce(input_text)
            elif "Tau Controlled English (TCE)" in input_type_str and "Tau Language" in output_type_str:
                print(f"Translating TCE to Tau: {input_text[:50]}...")
                result = self.translator.translate_tce_to_tau(input_text)
            # Add more conditions for English, IL once supported by the chosen translator
            else:
                self.output_text_edit.setText(f"Translation from '{input_type_str}' to '{output_type_str}' is not yet supported by this UI or translator.")
                return

            if result and result.success:
                self.output_text_edit.setText(result.output)
                # Optionally display confidence, patterns, warnings, errors from result object
                # print(f"Translation successful: {result.output}")
                # print(f"Confidence: {result.confidence}, Patterns: {result.patterns_detected}")
                # if result.warnings: print(f"Warnings: {result.warnings}")
                # if result.errors: print(f"Errors: {result.errors}")
            elif result:
                self.output_text_edit.setText(f"Translation failed: {result.errors or 'Unknown error'}")
            else:
                self.output_text_edit.setText("Translation produced no result.")
        
        except Exception as e:
            print(f"Exception during translation: {e}")
            self.output_text_edit.setText(f"An error occurred: {e}")

        # Create Settings Tab (moved to proper location)
        self.create_settings_tab()

    def create_settings_tab(self):
        """Create the settings tab with proper layout."""
        self.settings_tab = QWidget()
        self.tabs.addTab(self.settings_tab, "Settings")
        self.settings_layout = QVBoxLayout(self.settings_tab)
        # Placeholder content for Settings tab
        self.settings_layout.addWidget(QLabel("Settings Area (to be built, including Model Management)"))


def run_test_translations(window_instance):
    print("\n--- Running Automated UI Translation Tests ---")
    tests = [
        {
            "name": "TCE to Tau (Function)",
            "input_text": "define function myFunction as x + y",
            "input_type": "Tau Controlled English (TCE)",
            "output_type": "Tau Language"
        },
        {
            "name": "TCE to Tau (Rule)",
            "input_text": "rule: if a then b",
            "input_type": "Tau Controlled English (TCE)",
            "output_type": "Tau Language"
        },
        {
            "name": "Tau to TCE (Function)",
            "input_text": "myFunc() := z * 2",
            "input_type": "Tau Language",
            "output_type": "Tau Controlled English (TCE)"
        },
        {
            "name": "Tau to TCE (Always)",
            "input_text": "always x > 5",
            "input_type": "Tau Language",
            "output_type": "Tau Controlled English (TCE)"
        },
        {
            "name": "Unsupported: English to Tau",
            "input_text": "hello world",
            "input_type": "English",
            "output_type": "Tau Language"
        }
    ]

    for test in tests:
        print(f"\n--- Test: {test['name']} ---")
        print(f"Input Text: '{test['input_text']}'")
        print(f"Input Type: {test['input_type']}")
        print(f"Output Type: {test['output_type']}")
        
        window_instance.input_text_edit.setText(test['input_text'])
        window_instance.input_type_combo.setCurrentText(test['input_type'])
        window_instance.output_type_combo.setCurrentText(test['output_type'])
        
        # Call the handler
        window_instance.handle_translation()
        
        # Get output from UI
        ui_output = window_instance.output_text_edit.toPlainText()
        print(f"UI Output: '{ui_output}'")
        print("-------------------------------------")
    print("--- Automated UI Translation Tests Complete ---\n")

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    
    # Run test translations after window is shown but before app.exec
    # This allows UI elements to be ready
    # Note: This will run and print to console, then the UI will be interactive.
    # For a real test suite, you'd mock UI interactions or run headless.
    run_test_translations(main_window) 
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
