#!/usr/bin/env python3
"""
Integrated NLP Backend Server
============================

Unified backend server that integrates all NLP capabilities with consistent API.
Provides translation, autocomplete, validation, and explanation endpoints.

Author: DarklightX (Dana Edwards)
"""

import json
import logging
import time
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.integrated_nlp_system import NLPIntegrationAPI
from src.tau_translator_omega.core_engine.tgf_grammar_loader import TGFGrammarLoader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegratedNLPBackendHandler(BaseHTTPRequestHandler):
    """HTTP request handler for integrated NLP backend."""
    
    # Class-level NLP API instance (shared across requests)
    nlp_api = None
    grammar_loader = None
    
    @classmethod
    def initialize_nlp(cls):
        """Initialize NLP system once."""
        if cls.nlp_api is None:
            logger.info("Initializing NLP Integration API...")
            cls.nlp_api = NLPIntegrationAPI()
            cls.grammar_loader = TGFGrammarLoader()
            logger.info("NLP system initialized successfully")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.handle_health_check()
        elif parsed_path.path == '/api/nlp/capabilities':
            self.handle_capabilities()
        elif parsed_path.path == '/api/grammars':
            self.handle_list_grammars()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_path = urlparse(self.path)
        
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8')) if post_data else {}
            
            # Route to appropriate handler
            if parsed_path.path == '/translate':
                # Handle simple translate endpoint
                self.handle_simple_translate(data)
            elif parsed_path.path == '/api/translate':
                self.handle_translate(data)
            elif parsed_path.path == '/api/nlp/translate':
                self.handle_nlp_translate(data)
            elif parsed_path.path == '/api/nlp/autocomplete':
                self.handle_autocomplete(data)
            elif parsed_path.path == '/api/nlp/validate':
                self.handle_validate(data)
            elif parsed_path.path == '/api/nlp/explain':
                self.handle_explain(data)
            elif parsed_path.path == '/api/nlp/analyze':
                self.handle_analyze(data)
            else:
                self.send_error(404, "Not Found")
                
        except json.JSONDecodeError:
            self.send_json_response({
                "error": "Invalid JSON",
                "message": "Request body must be valid JSON"
            }, status=400)
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            self.send_json_response({
                "error": "Internal server error",
                "message": str(e)
            }, status=500)
    
    def handle_health_check(self):
        """Handle health check endpoint."""
        health_status = {
            "status": "healthy",
            "message": "Integrated NLP Backend is running",
            "timestamp": time.time(),
            "nlp_system": {
                "initialized": self.nlp_api is not None,
                "components": {
                    "translator": True,
                    "vocabulary": True,
                    "grammar": True,
                    "semantic_analyzer": True,
                    "incremental_parser": True,
                    "amr_analyzer": True,
                    "autocomplete": True
                }
            },
            "capabilities": [
                "translation",
                "autocomplete", 
                "validation",
                "explanation",
                "semantic_analysis"
            ]
        }
        
        self.send_json_response(health_status)
    
    def handle_capabilities(self):
        """Handle capabilities query."""
        capabilities = {
            "translation": {
                "languages": ["TCE", "TAU", "CNL", "PLAIN_ENGLISH"],
                "directions": [
                    {"from": "TCE", "to": "TAU"},
                    {"from": "TAU", "to": "TCE"},
                    {"from": "TAU", "to": "PLAIN_ENGLISH"}
                ],
                "nlp_enhancements": True
            },
            "autocomplete": {
                "enabled": True,
                "max_suggestions": 10
            },
            "validation": {
                "semantic_equivalence": True,
                "confidence_scoring": True
            },
            "explanation": {
                "languages": ["TAU", "TCE"],
                "natural_language": True
            },
            "analysis": {
                "semantic": True,
                "syntactic": True,
                "vocabulary": True
            }
        }
        
        self.send_json_response(capabilities)
    
    def handle_simple_translate(self, data):
        """Handle simple translate endpoint for working backend compatibility."""
        text = data.get("text", "")
        direction = data.get("direction", "tce_to_tau")
        
        if not text:
            self.send_json_response({
                "error": "Missing input",
                "message": "Text parameter is required"
            }, status=400)
            return
        
        try:
            # Map direction to source/target languages
            if direction == "tce_to_tau":
                source, target = "TCE", "TAU"
            elif direction == "tau_to_tce":
                source, target = "TAU", "TCE"
            else:
                # For other directions, extract from direction string
                parts = direction.split("_to_")
                if len(parts) == 2:
                    source = parts[0].upper()
                    target = parts[1].upper()
                else:
                    source, target = "TCE", "TAU"
            
            # Use NLP translate with direction mapping
            result = self.nlp_api.translate(text, source, target, use_nlp=True)
            
            # Format response for simple backend compatibility
            response = {
                "translatedText": result["translation"],
                "confidence": result["confidence"],
                "patterns": result.get("patterns_detected", []),
                "direction": direction,
                "provider": "NLP Enhanced",
                "secure": True
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Simple translation error: {e}")
            self.send_json_response({
                "error": "Translation failed",
                "message": str(e)
            }, status=500)
    
    def handle_translate(self, data):
        """Handle basic translation endpoint (backward compatibility)."""
        # Map to NLP translate
        data["use_nlp"] = data.get("use_nlp", True)
        self.handle_nlp_translate(data)
    
    def handle_nlp_translate(self, data):
        """Handle NLP-enhanced translation."""
        text = data.get("text", "")
        source = data.get("source", "TCE")
        target = data.get("target", "TAU")
        use_nlp = data.get("use_nlp", True)
        
        if not text:
            self.send_json_response({
                "error": "Missing input",
                "message": "Text parameter is required"
            }, status=400)
            return
        
        try:
            # Perform translation
            result = self.nlp_api.translate(text, source, target, use_nlp)
            
            # Format response
            response = {
                "success": True,
                "input": text,
                "translation": result["translation"],
                "confidence": result["confidence"],
                "source_language": source,
                "target_language": target,
                "nlp_enabled": use_nlp,
                "patterns_detected": result.get("patterns_detected", []),
                "execution_time": time.time()
            }
            
            # Include NLP enhancements if requested
            if data.get("include_details", False):
                response["nlp_details"] = result.get("nlp_enhancements", {})
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Translation failed",
                "message": str(e)
            }, status=500)
    
    def handle_autocomplete(self, data):
        """Handle autocomplete request."""
        text = data.get("text", "")
        cursor_position = data.get("cursor_position", len(text))
        max_suggestions = data.get("max_suggestions", 5)
        
        try:
            suggestions = self.nlp_api.autocomplete(text, cursor_position)
            
            response = {
                "success": True,
                "text": text,
                "cursor_position": cursor_position,
                "suggestions": suggestions[:max_suggestions]
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Autocomplete failed",
                "message": str(e)
            }, status=500)
    
    def handle_validate(self, data):
        """Handle translation validation."""
        original = data.get("original", "")
        translated = data.get("translated", "")
        
        if not original or not translated:
            self.send_json_response({
                "error": "Missing input",
                "message": "Both original and translated text are required"
            }, status=400)
            return
        
        try:
            validation_result = self.nlp_api.validate(original, translated)
            
            response = {
                "success": True,
                "original": original,
                "translated": translated,
                "validation": validation_result
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Validation failed",
                "message": str(e)
            }, status=500)
    
    def handle_explain(self, data):
        """Handle explanation generation."""
        text = data.get("text", "")
        language = data.get("language", "TAU")
        
        if not text:
            self.send_json_response({
                "error": "Missing input",
                "message": "Text parameter is required"
            }, status=400)
            return
        
        try:
            explanation = self.nlp_api.explain(text, language)
            
            response = {
                "success": True,
                "text": text,
                "language": language,
                "explanation": explanation
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Explanation error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Explanation failed",
                "message": str(e)
            }, status=500)
    
    def handle_analyze(self, data):
        """Handle comprehensive text analysis."""
        text = data.get("text", "")
        analysis_types = data.get("types", ["vocabulary", "semantic", "syntactic"])
        
        if not text:
            self.send_json_response({
                "error": "Missing input",
                "message": "Text parameter is required"
            }, status=400)
            return
        
        try:
            analysis_result = {}
            
            # Vocabulary analysis
            if "vocabulary" in analysis_types:
                analysis_result["vocabulary"] = self.nlp_api.nlp_system._enhance_with_vocabulary(text)
            
            # Semantic analysis
            if "semantic" in analysis_types:
                parse_result = self.nlp_api.nlp_system._incremental_parse(text)
                if "ast" in parse_result:
                    analysis_result["semantic"] = self.nlp_api.nlp_system._analyze_semantics(
                        text, parse_result["ast"]
                    )
            
            # Syntactic analysis
            if "syntactic" in analysis_types:
                analysis_result["syntactic"] = self.nlp_api.nlp_system._incremental_parse(text)
            
            response = {
                "success": True,
                "text": text,
                "analysis": analysis_result
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Analysis failed",
                "message": str(e)
            }, status=500)
    
    def handle_list_grammars(self):
        """Handle grammar listing."""
        try:
            grammars = list(self.nlp_api.nlp_system.loaded_grammars.keys())
            
            response = {
                "success": True,
                "grammars": grammars,
                "count": len(grammars)
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            logger.error(f"Grammar listing error: {e}")
            self.send_json_response({
                "success": False,
                "error": "Failed to list grammars",
                "message": str(e)
            }, status=500)
    
    def send_json_response(self, data, status=200):
        """Send JSON response with proper headers."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = json.dumps(data, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use logger instead of stderr."""
        logger.info(f"{self.client_address[0]} - {format % args}")


def run_server(port=8000):
    """Run the integrated NLP backend server."""
    # Initialize NLP system before starting server
    IntegratedNLPBackendHandler.initialize_nlp()
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, IntegratedNLPBackendHandler)
    
    logger.info(f"🚀 Integrated NLP Backend Server starting on port {port}")
    logger.info(f"📍 Health check: http://localhost:{port}/health")
    logger.info(f"📍 Capabilities: http://localhost:{port}/api/nlp/capabilities")
    logger.info(f"📍 Translation: POST http://localhost:{port}/api/nlp/translate")
    logger.info(f"📍 Autocomplete: POST http://localhost:{port}/api/nlp/autocomplete")
    logger.info(f"📍 Validation: POST http://localhost:{port}/api/nlp/validate")
    logger.info(f"📍 Explanation: POST http://localhost:{port}/api/nlp/explain")
    logger.info(f"📍 Analysis: POST http://localhost:{port}/api/nlp/analyze")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("\n🛑 Server shutting down...")
        httpd.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Integrated NLP Backend Server")
    parser.add_argument("--port", type=int, default=8000, help="Server port (default: 8000)")
    args = parser.parse_args()
    
    run_server(args.port)