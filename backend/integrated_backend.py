#!/usr/bin/env python3
"""
Fully Integrated Translation Backend
====================================

This backend properly integrates:
1. Grammar file loading from UI
2. Dynamic parser configuration
3. Grammar-driven translation
4. Proper error handling and fallbacks
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Import our enhanced components
from src.tau_translator_omega.core_engine.tgf_grammar_loader import get_grammar_loader
from src.tau_translator_omega.core_engine.enhanced_parser import GrammarAwareParser
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedTranslator:
    """Fully integrated translator with grammar support"""
    
    def __init__(self):
        self.grammar_loader = get_grammar_loader()
        self.parser = None
        self.translator = TCETauTranslator()
        self.fallback_mode = False
        
        # Initialize parser
        self._initialize_parser()
        
    def _initialize_parser(self):
        """Initialize parser with grammar loader"""
        try:
            self.parser = GrammarAwareParser(
                grammar_loader=self.grammar_loader,
                debug=False
            )
            
            # Test if parser works
            if self.parser.validate_grammar():
                logger.info("Grammar-aware parser initialized successfully")
                self.fallback_mode = False
            else:
                logger.warning("Parser validation failed, using fallback mode")
                self.fallback_mode = True
                
        except Exception as e:
            logger.error(f"Failed to initialize parser: {e}")
            self.fallback_mode = True
            self.parser = None
    
    def reload_grammar(self):
        """Reload grammar and reinitialize parser"""
        logger.info("Reloading grammar files...")
        
        # Reload grammar files
        self.grammar_loader.load_all_grammars()
        
        # Reinitialize parser
        self._initialize_parser()
        
        return not self.fallback_mode
    
    def translate(self, text: str, direction: str) -> Dict[str, Any]:
        """Translate with proper grammar support"""
        start_time = time.time()
        
        try:
            # Log translation request
            active_grammar = self.grammar_loader.get_active_grammar()
            logger.info(f"Translating '{text}' using grammar: {active_grammar.filename if active_grammar else 'default'}")
            
            if direction == "tce_to_tau":
                translated = self._translate_tce_to_tau(text)
            elif direction == "tau_to_tce":
                translated = self._translate_tau_to_tce(text)
            else:
                raise ValueError(f"Unknown direction: {direction}")
            
            processing_time = time.time() - start_time
            
            return {
                "translatedText": translated,
                "provider": "integrated_translator",
                "model": f"grammar:{active_grammar.filename if active_grammar else 'default'}",
                "processingTime": processing_time,
                "secure": True,
                "grammarBased": not self.fallback_mode
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            processing_time = time.time() - start_time
            
            # Try fallback
            if not self.fallback_mode:
                logger.info("Trying fallback translation...")
                self.fallback_mode = True
                return self.translate(text, direction)
            
            return {
                "translatedText": f"[Translation Error: {str(e)}]",
                "provider": "integrated_translator",
                "model": "error",
                "processingTime": processing_time,
                "secure": False,
                "error": str(e)
            }
    
    def _translate_tce_to_tau(self, text: str) -> str:
        """Translate TCE to Tau using grammar"""
        if self.fallback_mode or not self.parser:
            logger.warning("Using pattern-based fallback for TCE to Tau")
            return self._pattern_based_tce_to_tau(text)
        
        try:
            # Parse with grammar
            logger.debug(f"Parsing TCE: {text}")
            ast = self.parser.parse(text)
            
            # Translate AST
            logger.debug(f"Translating AST: {type(ast).__name__}")
            result = self.translator.translate(ast)
            
            return result.tau_code
            
        except Exception as e:
            logger.error(f"Grammar-based translation failed: {e}")
            # Fall back to pattern matching
            return self._pattern_based_tce_to_tau(text)
    
    def _translate_tau_to_tce(self, text: str) -> str:
        """Translate Tau to TCE"""
        # For now, use pattern-based translation
        # TODO: Implement proper Tau parser
        return self._pattern_based_tau_to_tce(text)
    
    def _pattern_based_tce_to_tau(self, text: str) -> str:
        """Fallback pattern-based TCE to Tau translation"""
        result = text.strip()
        
        # Remove trailing period
        if result.endswith('.'):
            result = result[:-1]
        
        # Basic replacements
        result = result.lower()
        result = result.replace(" and ", " & ")
        result = result.replace(" or ", " | ")
        result = result.replace(" not ", " ! ")
        
        # Handle temporal operators
        if result.startswith("always "):
            result = "always " + result[7:]
        elif result.startswith("sometimes "):
            result = "sometimes " + result[10:]
        elif result.startswith("eventually "):
            result = "eventually " + result[11:]
            
        # Add parentheses for complex expressions
        if any(op in result for op in [' & ', ' | ', ' -> ']):
            # Don't double-parenthesize
            if not (result.startswith('(') and result.endswith(')')):
                result = f"({result})"
                
        return result
    
    def _pattern_based_tau_to_tce(self, text: str) -> str:
        """Pattern-based Tau to TCE translation"""
        result = text.strip()
        
        # Remove parentheses
        if result.startswith('(') and result.endswith(')'):
            result = result[1:-1]
        
        # Basic replacements
        result = result.replace(" & ", " AND ")
        result = result.replace(" | ", " OR ")
        result = result.replace(" ! ", " NOT ")
        result = result.replace(" -> ", " IMPLIES ")
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
            
        # Add period
        if not result.endswith('.'):
            result += '.'
            
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get translator status"""
        active_grammar = self.grammar_loader.get_active_grammar()
        
        return {
            "initialized": self.parser is not None,
            "fallbackMode": self.fallback_mode,
            "activeGrammar": {
                "filename": active_grammar.filename if active_grammar else None,
                "type": active_grammar.type if active_grammar else None,
                "rules": len(active_grammar.rules) if active_grammar else 0
            },
            "loadedGrammars": list(self.grammar_loader.loaded_grammars.keys()),
            "parserInfo": self.parser.get_grammar_info() if self.parser else None
        }


# Global translator instance
translator = IntegratedTranslator()


class IntegratedHandler(BaseHTTPRequestHandler):
    """HTTP handler for integrated translation"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            status = translator.get_status()
            self.send_json_response({
                "status": "healthy",
                "service": "Integrated TauTranslator API",
                **status
            })
            
        elif parsed_path.path == '/status':
            self.send_json_response(translator.get_status())
            
        elif parsed_path.path == '/grammar/reload':
            success = translator.reload_grammar()
            self.send_json_response({
                "success": success,
                "message": "Grammar reloaded" if success else "Grammar reload failed",
                "status": translator.get_status()
            })
            
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if parsed_path.path == '/translate':
                self.handle_translate(data)
                
            elif parsed_path.path == '/grammar/set':
                self.handle_set_grammar(data)
                
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({
                "error": "Invalid request",
                "message": str(e)
            }, status=400)
    
    def handle_translate(self, data):
        """Handle translation request"""
        text = data.get('text', '')
        direction = data.get('direction', 'tce_to_tau')
        
        if not text:
            self.send_json_response({
                "error": "No text provided"
            }, status=400)
            return
        
        result = translator.translate(text, direction)
        self.send_json_response(result)
    
    def handle_set_grammar(self, data):
        """Handle grammar selection"""
        filename = data.get('filename')
        
        if not filename:
            self.send_json_response({
                "error": "Missing filename"
            }, status=400)
            return
        
        if translator.grammar_loader.set_active_grammar(filename):
            # Reload parser with new grammar
            success = translator.reload_grammar()
            
            self.send_json_response({
                "success": success,
                "message": f"Grammar set to {filename}" if success else f"Failed to load grammar {filename}",
                "status": translator.get_status()
            })
        else:
            self.send_json_response({
                "error": "Grammar file not found",
                "success": False
            }, status=404)
    
    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to reduce noise"""
        if '/health' not in args[0]:
            super().log_message(format, *args)


def run_server(port=8002):
    """Run the integrated backend server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, IntegratedHandler)
    
    logger.info(f"Integrated Backend running on port {port}")
    logger.info(f"Status: {json.dumps(translator.get_status(), indent=2)}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()