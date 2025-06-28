# Copyright (c) DarkLightX / Dana Edwards
"""
Semantic I/O services for vocabulary loading and logging.

This module provides classes that handle interactions with the file system
and environment variables for semantic analysis components, adhering to
the separation of I/O concerns.
"""

import json
import os
from typing import Dict, Any, Optional, List

class VocabularyLoader:
    """Handles vocabulary loading from external sources."""
    
    @staticmethod
    def load_from_file(file_path: str) -> Dict[str, Any]:
        """Load vocabulary from JSON file."""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading vocabulary from {file_path}: {e}") 
            return {'types': set(), 'predicates': {}, 'functions': {}}
    
    @staticmethod
    def load_from_environment() -> Dict[str, Any]:
        """Load vocabulary from environment variables."""
        vocab_path = os.environ.get('TAU_VOCABULARY_PATH')
        if vocab_path and os.path.exists(vocab_path):
            return VocabularyLoader.load_from_file(vocab_path)
        if not vocab_path:
            print("TAU_VOCABULARY_PATH environment variable not set.")
        elif not os.path.exists(vocab_path):
            print(f"TAU_VOCABULARY_PATH ({vocab_path}) does not exist.")
        return {'types': set(), 'predicates': {}, 'functions': {}}

class SemanticLogger:
    """Handles logging for semantic analysis."""
    
    def __init__(self, log_file: Optional[str] = None):
        """Initialize logger."""
        self.log_file = log_file
        self._enabled = log_file is not None
        if self._enabled and self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except OSError as e:
                    print(f"Error creating log directory {log_dir}: {e}")
                    self._enabled = False

    def log_analysis_start(self, node_type: str) -> None:
        """Log start of node analysis."""
        if self._enabled:
            self._write_log(f"Analyzing {node_type}")
    
    def log_error_found(self, error_message: str) -> None:
        """Log when error is found."""
        if self._enabled:
            self._write_log(f"Error found: {error_message}")
    
    def log_symbol_declared(self, symbol_name: str, symbol_type: str) -> None:
        """Log symbol declaration."""
        if self._enabled:
            self._write_log(f"Symbol declared: {symbol_name} ({symbol_type})")
    
    def _write_log(self, message: str) -> None:
        """Write message to log file."""
        if not self._enabled or not self.log_file:
            return
        try:
            with open(self.log_file, 'a') as f:
                f.write(f"{message}\n")
        except IOError as e:
            print(f"Error writing to log file {self.log_file}: {e}")
            pass
