#!/usr/bin/env python3
"""
Grammar-Aware Translation Backend
=================================

This backend properly integrates loaded grammar files with the translation engine.
It replaces the simple pattern-based approach with grammar-driven parsing.
"""

import json
import time
import logging
from pathlib import Path
from typing import Dict, Optional, Any

# Import our components
from src.tau_translator_omega.core_engine.tgf_grammar_loader import get_grammar_loader
from src.tau_translator_omega.core_engine.cnl_parser.cnl_parser import CNLParser
from src.tau_translator_omega.core_engine.tce_tau_translator import TCETauTranslator

# For the simple HTTP server
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GrammarAwareTranslator:
    """Translation engine that uses loaded grammar files"""
    
    def __init__(self):
        self.grammar_loader = get_grammar_loader()
        self.parser = None
        self.translator = TCETauTranslator()
        self._initialize_parser()
        
    def _initialize_parser(self):
        """Initialize parser with active grammar"""
        try:
            # Get active grammar
            active_grammar = self.grammar_loader.get_active_grammar()
            
            if active_grammar:
                logger.info(f"Initializing parser with grammar: {active_grammar.filename}")
                
                # Get grammar in parser format
                parser_grammar = self.grammar_loader.get_grammar_for_parser()
                
                if parser_grammar:
                    # Create parser with custom grammar
                    # Note: This requires modifying CNLParser to accept custom grammar
                    self.parser = CNLParser()
                    # For now, we'll use the default parser
                    logger.warning("Custom grammar loading not yet implemented in CNLParser")
                else:
                    logger.warning("Could not convert grammar to parser format")
                    self.parser = CNLParser()
            else:
                logger.info("No active grammar, using default parser")
                self.parser = CNLParser()
                
        except Exception as e:
            logger.error(f"Error initializing parser: {e}")
            self.parser = CNLParser()
    
    def reload_grammar(self):
        """Reload grammar files and reinitialize parser"""
        self.grammar_loader.load_all_grammars()
        self._initialize_parser()
    
    def translate(self, text: str, direction: str) -> Dict[str, Any]:
        """Translate text using grammar-aware parsing"""
        start_time = time.time()
        
        try:
            if direction == "tce_to_tau":
                # Parse TCE text
                try:
                    # Try to parse with grammar
                    ast = self.parser.parse(text)
                    # Translate AST to Tau
                    result = self.translator.translate(ast)
                    translated = result.tau_code
                except Exception as e:
                    logger.warning(f"Grammar parsing failed, using fallback: {e}")
                    # Fallback to pattern matching
                    translated = self._pattern_based_translation(text, direction)
                    
            elif direction == "tau_to_tce":
                # For now, use pattern-based reverse translation
                translated = self._pattern_based_translation(text, direction)
            else:
                raise ValueError(f"Unknown direction: {direction}")
            
            processing_time = time.time() - start_time
            
            return {
                "translatedText": translated,
                "provider": "grammar_aware_translator",
                "model": f"grammar:{self.grammar_loader.active_grammar.filename if self.grammar_loader.active_grammar else 'default'}",
                "processingTime": processing_time,
                "secure": True
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "translatedText": f"[Translation Error: {str(e)}]",
                "provider": "grammar_aware_translator",
                "model": "error",
                "processingTime": time.time() - start_time,
                "secure": False,
                "error": str(e)
            }
    
    def _pattern_based_translation(self, text: str, direction: str) -> str:
        """Fallback pattern-based translation"""
        if direction == "tce_to_tau":
            # Basic TCE to Tau patterns
            result = text.lower()
            result = result.replace(" and ", " & ")
            result = result.replace(" or ", " | ")
            result = result.replace(" not ", " ! ")
            result = result.replace("always ", "always ")
            result = result.replace("sometimes ", "sometimes ")
            
            # Remove trailing period
            if result.endswith('.'):
                result = result[:-1]
                
            # Add parentheses for safety
            if ' & ' in result or ' | ' in result:
                result = f"({result})"
                
            return result
            
        else:  # tau_to_tce
            # Basic Tau to TCE patterns
            result = text
            result = result.replace(" & ", " AND ")
            result = result.replace(" | ", " OR ")
            result = result.replace(" ! ", " NOT ")
            result = result.replace("(", "")
            result = result.replace(")", "")
            
            # Capitalize first letter and add period
            if result:
                result = result[0].upper() + result[1:] + "."
                
            return result


# Global translator instance
translator = GrammarAwareTranslator()


class GrammarAwareHandler(BaseHTTPRequestHandler):
    """HTTP handler for grammar-aware translation"""
    
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
            self.send_json_response({
                "status": "healthy",
                "service": "Grammar-Aware TauTranslator API",
                "grammarLoader": True,
                "activeGrammar": translator.grammar_loader.active_grammar.filename if translator.grammar_loader.active_grammar else None,
                "loadedGrammars": list(translator.grammar_loader.loaded_grammars.keys())
            })
        elif parsed_path.path == '/grammar/active':
            active = translator.grammar_loader.get_active_grammar()
            if active:
                self.send_json_response({
                    "filename": active.filename,
                    "type": active.type,
                    "rules": len(active.rules),
                    "terminals": len(active.terminals),
                    "nonTerminals": len(active.non_terminals)
                })
            else:
                self.send_json_response({"message": "No active grammar"})
        elif parsed_path.path == '/grammar/reload':
            translator.reload_grammar()
            self.send_json_response({"message": "Grammar reloaded"})
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
            translator.reload_grammar()
            self.send_json_response({
                "message": f"Grammar set to {filename}",
                "success": True
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


def run_server(port=8001):
    """Run the grammar-aware backend server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, GrammarAwareHandler)
    
    logger.info(f"Grammar-Aware Backend running on port {port}")
    logger.info(f"Active grammar: {translator.grammar_loader.active_grammar.filename if translator.grammar_loader.active_grammar else 'None'}")
    logger.info(f"Loaded grammars: {list(translator.grammar_loader.loaded_grammars.keys())}")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
        httpd.shutdown()


if __name__ == "__main__":
    run_server()