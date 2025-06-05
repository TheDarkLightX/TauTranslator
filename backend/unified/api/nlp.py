"""
NLP endpoints for the unified backend.

Handles NLP features like autocomplete, validation, and explanation (when NLP feature is enabled).

Author: DarkLightX / Dana Edwards
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..core.responses import create_success_response, create_error_response
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

router = APIRouter()

# Lazy loading of NLP components
_nlp_service = None

def get_nlp_service():
    """Get or create NLP service instance."""
    global _nlp_service
    if _nlp_service is None:
        try:
            from nlp.nlp_integration import NLPTranslationService
            _nlp_service = NLPTranslationService()
        except ImportError as e:
            # Return None if NLP is not available
            return None
    return _nlp_service


class AutocompleteRequest(BaseModel):
    text: str
    position: Optional[int] = None
    context: Optional[str] = None


class ValidationRequest(BaseModel):
    code: str
    language: str = "TAU"


class ExplainRequest(BaseModel):
    code: str
    language: str = "TAU"


@router.post("/autocomplete")
async def autocomplete(request: AutocompleteRequest):
    """Provide autocomplete suggestions."""
    try:
        nlp_service = get_nlp_service()
        
        if nlp_service is None:
            # Provide basic autocomplete without NLP
            basic_suggestions = get_basic_suggestions(request.text)
            return create_success_response({
                "suggestions": basic_suggestions,
                "source": "basic"
            })
        
        # Use NLP autocomplete engine
        suggestions = nlp_service.autocomplete_engine.get_completions(
            request.text, 
            max_results=10
        )
        
        formatted_suggestions = []
        for suggestion, confidence in suggestions:
            formatted_suggestions.append({
                "text": suggestion,
                "confidence": confidence,
                "type": determine_suggestion_type(suggestion)
            })
        
        return create_success_response({
            "suggestions": formatted_suggestions,
            "source": "nlp"
        })
        
    except Exception as e:
        return create_error_response(f"Autocomplete failed: {str(e)}")


@router.post("/validate")
async def validate_syntax(request: ValidationRequest):
    """Validate syntax and provide suggestions."""
    try:
        errors = []
        warnings = []
        
        # Basic syntax validation
        lines = request.code.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Check parentheses balance
            if line.count('(') != line.count(')'):
                errors.append({
                    "line": i + 1,
                    "message": "Unmatched parentheses",
                    "severity": "error"
                })
            
            # Check brackets balance
            if line.count('[') != line.count(']'):
                errors.append({
                    "line": i + 1,
                    "message": "Unmatched brackets",
                    "severity": "error"
                })
            
            # Check for TAU keywords without operators
            tau_keywords = ['DEFINE', 'always', 'sometimes', 'forall', 'exists']
            for keyword in tau_keywords:
                if keyword in line and not any(op in line for op in [':=', ':', '->', '<->']):
                    warnings.append({
                        "line": i + 1,
                        "message": f"Keyword '{keyword}' found without operator",
                        "severity": "warning"
                    })
        
        is_valid = len(errors) == 0
        
        # Get suggestions from NLP if available
        suggestions = []
        nlp_service = get_nlp_service()
        if nlp_service and not is_valid:
            # Generate fix suggestions
            for error in errors:
                if "parentheses" in error["message"]:
                    suggestions.append("Check parentheses matching")
                elif "brackets" in error["message"]:
                    suggestions.append("Check bracket matching")
        
        return create_success_response({
            "is_valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": suggestions
        })
        
    except Exception as e:
        return create_error_response(f"Validation failed: {str(e)}")


@router.post("/explain")
async def explain_code(request: ExplainRequest):
    """Explain code structure and meaning."""
    try:
        explanations = []
        lines = request.code.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            explanation = explain_line(line)
            if explanation:
                explanations.append({
                    "line": line,
                    "explanation": explanation
                })
        
        # Overall explanation
        overall = "This TAU code "
        if any('DEFINE' in e["line"] for e in explanations):
            overall += "defines concepts or functions"
        if any('always' in e["line"] or 'sometimes' in e["line"] for e in explanations):
            overall += ", uses temporal logic"
        if any('forall' in e["line"] or 'exists' in e["line"] for e in explanations):
            overall += ", and includes quantifiers"
        overall += "."
        
        return create_success_response({
            "explanation": overall,
            "line_explanations": explanations
        })
        
    except Exception as e:
        return create_error_response(f"Explanation failed: {str(e)}")


def get_basic_suggestions(text: str) -> List[Dict[str, str]]:
    """Get basic autocomplete suggestions without NLP."""
    suggestions = []
    
    # TAU keywords
    keywords = ['DEFINE', 'CONCEPT', 'always', 'sometimes', 'eventually', 
                'forall', 'exists', 'true', 'false']
    
    # TAU operators
    operators = [':=', '->', '<->', '&&', '||', '!', '=', '!=', '>', '<', '>=', '<=']
    
    # Filter based on partial match
    text_lower = text.lower()
    for keyword in keywords:
        if keyword.lower().startswith(text_lower):
            suggestions.append({
                "text": keyword,
                "type": "keyword"
            })
    
    for operator in operators:
        if operator.startswith(text):
            suggestions.append({
                "text": operator,
                "type": "operator"
            })
    
    return suggestions[:10]  # Limit to 10 suggestions


def determine_suggestion_type(suggestion: str) -> str:
    """Determine the type of suggestion."""
    if suggestion in ['always', 'sometimes', 'eventually', 'never']:
        return "temporal"
    elif suggestion in ['forall', 'exists']:
        return "quantifier"
    elif suggestion in ['DEFINE', 'CONCEPT', 'FUNCTION']:
        return "keyword"
    elif suggestion in ['->', '<->', '&&', '||', '!', ':=']:
        return "operator"
    else:
        return "identifier"


def explain_line(line: str) -> Optional[str]:
    """Generate explanation for a single line of code."""
    if 'DEFINE' in line:
        return "Defines a new concept or function"
    elif 'always' in line:
        return "States that something is always true"
    elif 'sometimes' in line:
        return "States that something is sometimes true"
    elif 'eventually' in line:
        return "States that something will eventually be true"
    elif 'forall' in line:
        return "Universal quantification - true for all values"
    elif 'exists' in line:
        return "Existential quantification - true for at least one value"
    elif '->' in line:
        return "Logical implication"
    elif '<->' in line:
        return "Logical equivalence (if and only if)"
    elif ':=' in line:
        return "Definition or assignment"
    return None