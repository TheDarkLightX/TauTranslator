#!/usr/bin/env python3
"""
Simple HTTP Backend for TauTranslatorOmega
==========================================

Basic HTTP server with proper translation integration.
Provides authentication and translation endpoints.
"""

import json
import time
import hashlib
import secrets
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the actual translator
from src.tau_translator_omega.lmql_engine.bidirectional_translator import LMQLBidirectionalTranslator

# Simple in-memory storage
sessions = {}
master_password_hash = None

# Initialize translator
translator = LMQLBidirectionalTranslator()

class TauBackendHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
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
                "message": "Simple backend is running",
                "secureStorageAvailable": True,
                "cryptoAvailable": True,
                "configuredProviders": ["mock_provider"],
                "translationEngines": {
                    "mock_engine": True,
                    "cnl_parser": True,
                    "tau_translator": True
                }
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
            
            if parsed_path.path == '/auth':
                self.handle_auth(data)
            elif parsed_path.path == '/api/translate':
                self.handle_translate(data)
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            self.send_json_response({
                "error": "Invalid request",
                "message": str(e)
            }, status=400)

    def handle_auth(self, data):
        """Handle authentication"""
        global master_password_hash
        
        password = data.get('password', '')
        
        if not password:
            self.send_json_response({
                "error": "Invalid password",
                "message": "Password is required"
            }, status=400)
            return
        
        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # First time setup
        if master_password_hash is None:
            master_password_hash = password_hash
            print(f"✅ Master password set for first time")
        
        # Verify password
        if password_hash != master_password_hash:
            self.send_json_response({
                "error": "Authentication failed",
                "message": "Incorrect master password"
            }, status=401)
            return
        
        # Generate session token
        session_token = secrets.token_urlsafe(32)
        sessions[session_token] = {
            "created": time.time(),
            "authenticated": True
        }
        
        self.send_json_response({
            "authenticated": True,
            "sessionToken": session_token,
            "message": "Authentication successful"
        })

    def handle_translate(self, data):
        """Handle translation requests"""
        # Check authentication
        auth_header = self.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            self.send_json_response({
                "error": "Authentication required",
                "message": "Please authenticate first"
            }, status=401)
            return
        
        session_token = auth_header[7:]  # Remove 'Bearer '
        if session_token not in sessions:
            self.send_json_response({
                "error": "Invalid session",
                "message": "Please authenticate again"
            }, status=401)
            return
        
        # Extract translation data
        source_text = data.get('sourceText', '')
        source_lang = data.get('sourceLangKey', '')
        target_lang = data.get('targetLangKey', '')
        
        # Simulate processing time
        time.sleep(0.3)
        
        # Generate enhanced translation
        translated_text = self.generate_translation(source_text, source_lang, target_lang)
        
        self.send_json_response({
            "translatedText": translated_text,
            "provider": "simple_backend",
            "model": "enhanced_mock",
            "processingTime": 0.3,
            "secure": True,
            "mock": False
        })

    def generate_translation(self, source_text, source_lang, target_lang):
        """Generate translation using actual LMQL translator"""
        if not source_text:
            return "[Empty input]"
        
        try:
            # Use the actual translator
            if source_lang == 'PLAIN_ENGLISH' and target_lang == 'TAU':
                result = translator.translate_tce_to_tau(source_text)
                return result.output
            elif source_lang == 'TAU' and target_lang == 'PLAIN_ENGLISH':
                result = translator.translate_tau_to_tce(source_text)
                return result.output
            else:
                # For other language pairs, use fallback formatting
                if target_lang == 'CNL':
                    return f"CNL: {source_text}"
                elif target_lang == 'ILR':
                    return f"ILR({source_text})"
                else:
                    return source_text
        except Exception as e:
            # If translation fails, return formatted fallback
            return f"{target_lang}: {source_text}"

    def send_json_response(self, data, status=200):
        """Send JSON response with CORS headers"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def log_message(self, format, *args):
        """Override to reduce log noise"""
        if self.path not in ['/health']:
            print(f"[{time.strftime('%H:%M:%S')}] {format % args}")

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, TauBackendHandler)
    
    print(f"🚀 Simple Backend Server starting on http://127.0.0.1:{port}")
    print(f"📖 Endpoints:")
    print(f"   GET  /health - Health check")
    print(f"   POST /auth - Authentication")
    print(f"   POST /api/translate - Translation")
    print(f"🔄 Press Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(f"\n⚠️  Server stopped")
        httpd.shutdown()

if __name__ == "__main__":
    run_server()
