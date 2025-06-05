#!/usr/bin/env python3
"""
TauTranslator Production-Ready Implementation
============================================

Consolidated, production-ready translator with proper error handling,
logging, and fallback mechanisms.

Copyright (c) 2024 TauTranslatorOmega Team
"""

import sys
import os
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Try importing core modules with fallback
try:
    from src.tau_translator_omega.lmql_engine.bidirectional_translator import (
        LMQLBidirectionalTranslator, 
        TranslationDirection,
        TranslationResult
    )
    CORE_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")
    CORE_AVAILABLE = False

# Production configuration
class Config:
    """Production configuration settings."""
    
    # API Configuration
    API_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    
    # Model Configuration
    DEFAULT_MODEL = "gpt-3.5-turbo"
    FALLBACK_MODEL = "pattern-based"
    
    # Security
    ENCRYPT_KEYS = True
    KEY_FILE = Path.home() / ".tau_translator" / "api_keys.enc"
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FILE = "tau_translator.log"
    
    # Features
    ENABLE_WEB_UI = True
    ENABLE_CLI = True
    ENABLE_API = True
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        config = cls()
        
        # Override from environment
        config.API_TIMEOUT = int(os.getenv("TAU_API_TIMEOUT", config.API_TIMEOUT))
        config.DEFAULT_MODEL = os.getenv("TAU_DEFAULT_MODEL", config.DEFAULT_MODEL)
        config.LOG_LEVEL = os.getenv("TAU_LOG_LEVEL", config.LOG_LEVEL)
        
        return config


class ProductionTranslator:
    """Production-ready Tau translator with all safety features."""
    
    def __init__(self, config: Config = None):
        """Initialize the production translator."""
        self.config = config or Config.from_env()
        self._setup_logging()
        self._initialize_translator()
        
    def _setup_logging(self):
        """Configure production logging."""
        log_level = getattr(logging, self.config.LOG_LEVEL.upper())
        
        # File handler
        if self.config.LOG_FILE:
            file_handler = logging.FileHandler(self.config.LOG_FILE)
            file_handler.setLevel(log_level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        logger.setLevel(log_level)
        
    def _initialize_translator(self):
        """Initialize the core translator with fallbacks."""
        if CORE_AVAILABLE:
            try:
                self.translator = LMQLBidirectionalTranslator()
                logger.info("Core translator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize core translator: {e}")
                self.translator = None
        else:
            logger.warning("Core translator not available, using fallback")
            self.translator = None
            
    def translate(self, text: str, direction: str = "tau_to_tce") -> Dict[str, Any]:
        """
        Main translation method with full error handling.
        
        Args:
            text: Input text to translate
            direction: Translation direction ("tau_to_tce" or "tce_to_tau")
            
        Returns:
            Dictionary with translation results
        """
        try:
            # Validate input
            if not text or not text.strip():
                return {
                    "success": False,
                    "error": "Empty input text",
                    "output": ""
                }
            
            # Use core translator if available
            if self.translator:
                if direction == "tau_to_tce":
                    result = self.translator.translate_tau_to_tce(text)
                else:
                    result = self.translator.translate_tce_to_tau(text)
                
                return {
                    "success": result.success,
                    "output": result.output,
                    "confidence": result.confidence,
                    "patterns": result.patterns_detected,
                    "errors": result.errors,
                    "warnings": result.warnings
                }
            else:
                # Use fallback pattern-based translation
                return self._fallback_translate(text, direction)
                
        except Exception as e:
            logger.error(f"Translation error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }
    
    def _fallback_translate(self, text: str, direction: str) -> Dict[str, Any]:
        """Fallback translation using simple patterns."""
        logger.info("Using fallback pattern-based translation")
        
        if direction == "tau_to_tce":
            # Simple Tau to TCE patterns
            patterns = {
                r'always\s+(.+)': 'Always {0}.',
                r'sometimes\s+(.+)': 'Sometimes {0}.',
                r'(\w+)\s*:=\s*(.+)': 'Define {0} as {1}.',
                r'r\s+(\w+)\[(\w+)\]\s*=\s*(.+)': 'Rule: {0} at time {1} equals {2}.',
                r'sbf\s+(\w+)\s*=\s*ifile\("([^"]+)"\)': 'Input stream {0} reads from file {1}.',
                r'sbf\s+(\w+)\s*=\s*ofile\("([^"]+)"\)': 'Output stream {0} writes to file {1}.',
            }
            
            output = text
            for pattern, template in patterns.items():
                import re
                matches = re.findall(pattern, output)
                for match in matches:
                    if isinstance(match, tuple):
                        replacement = template.format(*match)
                    else:
                        replacement = template.format(match)
                    output = re.sub(pattern, replacement, output, count=1)
                    
            return {
                "success": True,
                "output": output,
                "confidence": 0.6,
                "patterns": ["fallback"],
                "errors": [],
                "warnings": ["Using fallback translation - results may be less accurate"]
            }
        else:
            # Simple TCE to Tau patterns
            patterns = {
                r'Always\s+(.+)\.': 'always {0}',
                r'Sometimes\s+(.+)\.': 'sometimes {0}',
                r'Define\s+(\w+)\s+as\s+(.+)\.': '{0} := {1}',
                r'Rule:\s+(\w+)\s+at\s+time\s+(\w+)\s+equals\s+(.+)\.': 'r {0}[{1}] = {2}',
                r'Input\s+stream\s+(\w+)\s+reads\s+from\s+file\s+([^\s]+)\.': 'sbf {0} = ifile("{1}")',
                r'Output\s+stream\s+(\w+)\s+writes\s+to\s+file\s+([^\s]+)\.': 'sbf {0} = ofile("{1}")',
            }
            
            output = text
            for pattern, template in patterns.items():
                import re
                matches = re.findall(pattern, output, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        replacement = template.format(*match)
                    else:
                        replacement = template.format(match)
                    output = re.sub(pattern, replacement, output, count=1, flags=re.IGNORECASE)
                    
            return {
                "success": True,
                "output": output,
                "confidence": 0.6,
                "patterns": ["fallback"],
                "errors": [],
                "warnings": ["Using fallback translation - results may be less accurate"]
            }


def main():
    """Command-line interface for the production translator."""
    parser = argparse.ArgumentParser(
        description="TauTranslator - Production Ready Tau ↔ TCE Translation"
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Input text to translate (or use --file)"
    )
    
    parser.add_argument(
        "-d", "--direction",
        choices=["tau_to_tce", "tce_to_tau"],
        default="tau_to_tce",
        help="Translation direction"
    )
    
    parser.add_argument(
        "-f", "--file",
        help="Input file to translate"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    parser.add_argument(
        "--web",
        action="store_true",
        help="Start web interface"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Start API server"
    )
    
    args = parser.parse_args()
    
    # Initialize translator
    translator = ProductionTranslator()
    
    # Handle web interface
    if args.web:
        logger.info("Starting web interface...")
        try:
            from tau_translator_omega.web_interface.app import app
            app.run(host="0.0.0.0", port=5000, debug=False)
        except ImportError:
            logger.error("Web interface not available. Install Flask: pip install flask")
        return
    
    # Handle API server
    if args.api:
        logger.info("Starting API server...")
        try:
            import uvicorn
            uvicorn.run(
                "backend_server:app",
                host="0.0.0.0",
                port=8000,
                log_level="info"
            )
        except ImportError:
            logger.error("API server not available. Install FastAPI: pip install fastapi uvicorn")
        return
    
    # Handle translation
    if args.file:
        with open(args.file, 'r') as f:
            input_text = f.read()
    elif args.input:
        input_text = args.input
    else:
        # Interactive mode
        print("TauTranslator Production Ready")
        print("Enter text to translate (Ctrl+D to finish):")
        input_text = sys.stdin.read()
    
    # Perform translation
    result = translator.translate(input_text, args.direction)
    
    # Format output
    if args.json:
        output = json.dumps(result, indent=2)
    else:
        if result["success"]:
            output = result["output"]
            if result.get("warnings"):
                output += "\n\nWarnings:\n" + "\n".join(f"- {w}" for w in result["warnings"])
        else:
            output = f"Translation failed: {result.get('error', 'Unknown error')}"
            if result.get("errors"):
                output += "\n\nErrors:\n" + "\n".join(f"- {e}" for e in result["errors"])
    
    # Write output
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        logger.info(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()