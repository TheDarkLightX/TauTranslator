"""
TauTranslatorOmega Web Interface
===============================

Flask-based web interface for bidirectional Tau ↔ TCE translation.
Demonstrates the LMQL-powered translation capabilities.
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ..lmql_engine.bidirectional_translator import (
    LMQLBidirectionalTranslator, 
    TranslationDirection
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tau-translator-omega-demo'

# Initialize the translator
translator = LMQLBidirectionalTranslator()

@app.route('/')
def index():
    """Main page with bidirectional translation interface."""
    return render_template('index.html', 
                         lmql_available=translator.use_lmql)

@app.route('/translate', methods=['POST'])
def translate():
    """API endpoint for translation."""
    try:
        data = request.get_json()
        
        text = data.get('text', '').strip()
        direction = data.get('direction', 'tau_to_tce')
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'No text provided'
            })
        
        # Perform translation
        if direction == 'tau_to_tce':
            result = translator.translate_tau_to_tce(text)
        elif direction == 'tce_to_tau':
            result = translator.translate_tce_to_tau(text)
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid direction'
            })
        
        return jsonify({
            'success': result.success,
            'output': result.output,
            'confidence': result.confidence,
            'patterns_detected': result.patterns_detected,
            'errors': result.errors,
            'warnings': result.warnings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/examples')
def examples():
    """Get example translations."""
    tau_examples = [
        {
            'tau': 'halfAdderSum(a, b) := a + b',
            'tce': 'Define function halfAdderSum as a plus b',
            'description': 'Function definition for half adder sum'
        },
        {
            'tau': 'r o1[t] = i1[t] & i2[t]',
            'tce': 'Rule: o1 at time t equals i1 at time t and i2 at time t',
            'description': 'Logic gate rule with temporal reference'
        },
        {
            'tau': 'sbf i1 = ifile("data.in")',
            'tce': 'Input stream i1 reads from file data.in',
            'description': 'Stream input declaration'
        },
        {
            'tau': 'always (x > 0)',
            'tce': 'Always x is greater than zero',
            'description': 'Temporal logic constraint'
        }
    ]
    
    return jsonify({
        'examples': tau_examples,
        'lmql_available': translator.use_lmql
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'translator_ready': True,
        'lmql_available': translator.use_lmql
    })

if __name__ == '__main__':
    print("🚀 Starting TauTranslatorOmega Web Interface")
    print(f"🔧 LMQL Available: {translator.use_lmql}")
    print("📡 Server will be available at: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
