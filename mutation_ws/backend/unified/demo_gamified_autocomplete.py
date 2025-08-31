"""
Demo script for the gamified educational autocomplete system.

Shows how to use the complete gamification system with TauTranslator.

Copyright: DarkLightX / Dana Edwards
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from backend.unified.ui.gamified_autocomplete_widget import GamifiedAutocompleteWindow

def main():
    """Run the gamified autocomplete demo."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("TauTranslator Gamified Learning")
    app.setOrganizationName("DarkLightX")
    
    # Apply modern styling
    app.setStyle("Fusion")
    
    # Custom stylesheet for better appearance
    app.setStyleSheet("""
        QMainWindow {
            background-color: #F5F5F5;
        }
        
        QTextEdit {
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            padding: 10px;
            background-color: white;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        
        QListWidget {
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            background-color: white;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #EEEEEE;
        }
        
        QListWidget::item:hover {
            background-color: #E3F2FD;
        }
        
        QListWidget::item:selected {
            background-color: #2196F3;
            color: white;
        }
        
        QPushButton {
            padding: 8px 16px;
            border: 1px solid #CCCCCC;
            border-radius: 4px;
            background-color: white;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #F5F5F5;
            border-color: #999999;
        }
        
        QPushButton:pressed {
            background-color: #E0E0E0;
        }
        
        QPushButton:checked {
            background-color: #2196F3;
            color: white;
            border-color: #1976D2;
        }
        
        QProgressBar {
            border: 1px solid #CCCCCC;
            border-radius: 3px;
            text-align: center;
            height: 20px;
        }
        
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 2px;
        }
        
        QLabel {
            color: #333333;
        }
        
        QStatusBar {
            background-color: #EEEEEE;
            border-top: 1px solid #CCCCCC;
        }
        
        QToolBar {
            background-color: #FAFAFA;
            border-bottom: 1px solid #CCCCCC;
            spacing: 10px;
            padding: 5px;
        }
    """)
    
    # Create and show the main window
    window = GamifiedAutocompleteWindow()
    
    # Show demo message
    from PyQt6.QtWidgets import QMessageBox
    welcome = QMessageBox()
    welcome.setWindowTitle("Welcome to Gamified TauTranslator!")
    welcome.setText(
        "Learn formal specification with gamification!\n\n"
        "• Earn XP for using autocomplete suggestions\n"
        "• Complete daily challenges\n"
        "• Unlock achievements\n"
        "• Track your progress\n\n"
        "Start typing to see intelligent suggestions!"
    )
    welcome.setIcon(QMessageBox.Icon.Information)
    welcome.exec()
    
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()