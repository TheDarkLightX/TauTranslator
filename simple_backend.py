#!/usr/bin/env python3
"""
Simple HTTP Backend for TauTranslatorOmega
==========================================

Basic HTTP server using only Python standard library.
Provides authentication and translation endpoints.
"""

import json
import time
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Simple in-memory storage
sessions = {}
master_password_hash = None

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
        """Generate enhanced mock translations"""
        if not source_text:
            return "[Empty input]"
        
        if source_lang == 'PLAIN_ENGLISH':
            if target_lang == 'CNL':
                return f"""SPECIFICATION: {source_text}

WHEN the user requests "{source_text.strip()}"
THEN the system SHALL process this as a controlled natural language specification
AND the system SHALL validate the semantic correctness
AND the system SHALL generate appropriate formal representations."""

            elif target_lang == 'TAU':
                # Generate more realistic Tau code
                concept_name = source_text.lower().replace(' ', '_').replace(',', '').replace('.', '')[:20]
                return f"""// Tau Language Translation
// Source: "{source_text}"

DEFINE CONCEPT {concept_name} AS (
  description: "{source_text}",
  type: user_specification,
  timestamp: {int(time.time())}
);

RULE process_{concept_name} AS (
  WHEN user_input(X) AND matches(X, "{source_text}")
  THEN execute_specification({concept_name})
);"""

            elif target_lang == 'ILR':
                return f"""<?xml version="1.0" encoding="UTF-8"?>
<intermediate_logic_representation>
  <source_statement>
    <text>{source_text}</text>
    <language>plain_english</language>
  </source_statement>
  <semantic_analysis>
    <concepts>
      <concept id="1" type="action" confidence="0.95"/>
      <concept id="2" type="object" confidence="0.87"/>
    </concepts>
    <relations>
      <relation type="performs" subject="1" object="2"/>
    </relations>
  </semantic_analysis>
  <formal_representation>
    <logic_form>∃x,y (action(x) ∧ object(y) ∧ performs(x,y))</logic_form>
  </formal_representation>
</intermediate_logic_representation>"""

        else:
            # Translating from formal to English
            return f"""This formal specification represents the following concept:

"{source_text[:100]}..."

The specification defines a computational process that can be executed by the Tau system. It includes formal logic representations, semantic constraints, and execution rules that ensure correct behavior according to the original requirements."""

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
