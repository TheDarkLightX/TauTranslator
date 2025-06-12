"""
Centralized logging configuration for TauTranslatorOmega.

This module provides consistent logging setup across all components,
replacing debug print statements with proper structured logging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


class TauLogger:
    """Centralized logger factory for TauTranslatorOmega components."""
    
    _configured = False
    _log_level = logging.INFO
    
    @classmethod
    def configure(cls, log_level: int = logging.INFO, log_file: Optional[Path] = None) -> None:
        """Configure logging for the entire application."""
        if cls._configured:
            return
            
        cls._log_level = log_level
        
        # Create formatter
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Configure root logger
        root_logger = logging.getLogger('tau_translator_omega')
        root_logger.setLevel(log_level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # File handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        cls._configured = True
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get a logger for a specific component."""
        if not cls._configured:
            cls.configure()
        
        return logging.getLogger(f'tau_translator_omega.{name}')


def get_component_logger(component_name: str) -> logging.Logger:
    """Get a logger for a specific component (convenience function)."""
    return TauLogger.get_logger(component_name)


# Pre-configured loggers for common components
plugin_manager_logger = get_component_logger('plugin_manager')
preprocessor_logger = get_component_logger('preprocessor')
parser_logger = get_component_logger('parser')
validator_logger = get_component_logger('validator')
