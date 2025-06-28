# Copyright (c) DarkLightX / Dana Edwards
"""
Grammar I/O Repository
======================

This module provides an infrastructure-layer repository for handling all
I/O operations related to grammar files and their configurations.

It is responsible for reading and writing from the file system and abstracts
these details away from the core application and domain logic, ensuring the
core remains pure and testable.

Responsibilities:
- Reading the main grammar configuration file (e.g., 'grammar-files.json').
- Reading the content of individual grammar files (.tgf, .lark).
- Writing updated configurations back to the file system.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Union

from returns.result import Result, Success, Failure

logger = logging.getLogger(__name__)


class GrammarRepository:
    """Manages file system access for grammar files and configurations."""

    def __init__(self, grammar_dir: Path, config_file: Path):
        self.grammar_dir = grammar_dir
        self.config_file = config_file

    def read_grammar_config(self) -> Result[List[Dict[str, Any]], str]:
        """Reads the grammar configuration file from the file system.

        Returns:
            A Result containing the list of grammar configurations on success,
            or an error message string on failure.
        """
        if not self.config_file.exists():
            logger.warning(f"Grammar config file not found: {self.config_file}")
            return Success([])  # Return empty list if not found, not a hard error

        try:
            with self.config_file.open('r') as f:
                return Success(json.load(f))
        except (IOError, json.JSONDecodeError) as e:
            error_msg = f"Error reading or parsing grammar config '{self.config_file}': {e}"
            logger.error(error_msg)
            return Failure(error_msg)

    def read_grammar_file(self, filename: str) -> Result[str, str]:
        """Reads the content of a single grammar file.

        Args:
            filename: The name of the grammar file to read.

        Returns:
            A Result containing the file content on success, or an error message on failure.
        """
        file_path = self.grammar_dir / filename
        if not file_path.exists():
            error_msg = f"Grammar file not found: {file_path}"
            logger.warning(error_msg)
            return Failure(error_msg)

        try:
            with file_path.open('r') as f:
                return Success(f.read())
        except IOError as e:
            error_msg = f"Error reading grammar file '{file_path}': {e}"
            logger.error(error_msg)
            return Failure(error_msg)

    def write_grammar_config(self, config_data: List[Dict[str, Any]]) -> Result[None, str]:
        """Writes the grammar configuration data to the file system.

        Args:
            config_data: The list of grammar configurations to write.

        Returns:
            A Result containing None on success, or an error message on failure.
        """
        try:
            with self.config_file.open('w') as f:
                json.dump(config_data, f, indent=2)
            return Success(None)
        except IOError as e:
            error_msg = f"Error writing grammar config to '{self.config_file}': {e}"
            logger.error(error_msg)
            return Failure(error_msg)
