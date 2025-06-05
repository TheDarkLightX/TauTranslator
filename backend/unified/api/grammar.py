"""
Grammar management endpoints for the unified backend.

Handles grammar loading, validation, and switching (when grammar feature is enabled).

Author: DarkLightX / Dana Edwards
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from pathlib import Path
import json
from typing import List, Dict, Optional
from ..core.responses import create_success_response, create_error_response
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Grammar file cache
_grammar_cache: Dict[str, Dict] = {}

def get_available_grammars() -> List[Dict]:
    """Get list of available grammar files."""
    grammar_dir = settings.grammar_dir
    grammars = []
    
    if grammar_dir.exists():
        # Look for .tgf (Tau Grammar Format) and .ebnf files
        for ext in ['*.tgf', '*.ebnf', '*.lark']:
            for grammar_file in grammar_dir.glob(ext):
                grammars.append({
                    "name": grammar_file.stem,
                    "filename": grammar_file.name,
                    "path": str(grammar_file),
                    "format": grammar_file.suffix[1:],  # Remove the dot
                    "size": grammar_file.stat().st_size
                })
    
    return grammars


@router.get("/")
async def list_grammars():
    """List available grammar files."""
    try:
        grammars = get_available_grammars()
        
        # Check if we have an active grammar
        active_grammar = None
        grammar_config_file = settings.project_root / "config" / "grammar-files.json"
        if grammar_config_file.exists():
            with open(grammar_config_file) as f:
                config = json.load(f)
                active_grammar = config.get("active_grammar")
        
        return create_success_response({
            "grammars": grammars,
            "active_grammar": active_grammar,
            "grammar_dir": str(settings.grammar_dir)
        })
    except Exception as e:
        return create_error_response(f"Failed to list grammars: {str(e)}")


@router.get("/{grammar_name}")
async def get_grammar(grammar_name: str):
    """Get details about a specific grammar."""
    try:
        # Check cache first
        if grammar_name in _grammar_cache:
            return create_success_response(_grammar_cache[grammar_name])
        
        # Find the grammar file
        grammar_dir = settings.grammar_dir
        grammar_file = None
        
        for ext in ['.tgf', '.ebnf', '.lark']:
            potential_file = grammar_dir / f"{grammar_name}{ext}"
            if potential_file.exists():
                grammar_file = potential_file
                break
        
        if not grammar_file:
            raise HTTPException(status_code=404, detail=f"Grammar '{grammar_name}' not found")
        
        # Read grammar content
        content = grammar_file.read_text()
        
        # Parse metadata if available
        metadata = {
            "name": grammar_name,
            "filename": grammar_file.name,
            "format": grammar_file.suffix[1:],
            "size": grammar_file.stat().st_size,
            "content": content,
            "rules": extract_grammar_rules(content, grammar_file.suffix[1:])
        }
        
        # Cache the result
        _grammar_cache[grammar_name] = metadata
        
        return create_success_response(metadata)
        
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(f"Failed to get grammar details: {str(e)}")


@router.post("/load-from-path")
async def load_grammar_from_path(request: Request, grammar_path: str):
    """Load a Tau grammar from a file path on the server."""
    try:
        if not hasattr(request.app.state, 'grammar_engine'):
            raise HTTPException(
                status_code=503,
                detail="Grammar engine not available"
            )
        
        grammar_engine = request.app.state.grammar_engine
        
        # Validate path
        path = Path(grammar_path)
        if not path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Grammar file not found: {grammar_path}"
            )
        
        if not path.suffix in ['.lark', '.ebnf', '.tgf']:
            raise HTTPException(
                status_code=400,
                detail="Invalid file format"
            )
        
        # Load the grammar
        success = grammar_engine.load_tau_grammar(grammar_path)
        
        if success:
            return create_success_response({
                "message": "Grammar loaded successfully",
                "path": grammar_path
            })
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to load grammar"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(f"Failed to load grammar: {str(e)}")


@router.post("/reload")
async def reload_grammar():
    """Reload grammar files and clear cache."""
    try:
        # Clear grammar cache
        _grammar_cache.clear()
        
        # Re-scan grammar directory
        grammars = get_available_grammars()
        
        # If we have a grammar loader, reinitialize it
        # This would be done through the translation manager
        
        return create_success_response({
            "message": "Grammar files reloaded successfully",
            "grammars_found": len(grammars),
            "grammars": grammars
        })
        
    except Exception as e:
        return create_error_response(f"Failed to reload grammars: {str(e)}")


@router.post("/{grammar_name}/activate")
async def activate_grammar(grammar_name: str):
    """Set a grammar as the active grammar."""
    try:
        # Verify grammar exists
        grammars = get_available_grammars()
        grammar_names = [g["name"] for g in grammars]
        
        if grammar_name not in grammar_names:
            raise HTTPException(status_code=404, detail=f"Grammar '{grammar_name}' not found")
        
        # Update configuration
        grammar_config_file = settings.project_root / "config" / "grammar-files.json"
        config = {}
        
        if grammar_config_file.exists():
            with open(grammar_config_file) as f:
                config = json.load(f)
        
        config["active_grammar"] = grammar_name
        
        # Save configuration
        grammar_config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(grammar_config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        return create_success_response({
            "message": f"Grammar '{grammar_name}' activated successfully",
            "active_grammar": grammar_name
        })
        
    except HTTPException:
        raise
    except Exception as e:
        return create_error_response(f"Failed to activate grammar: {str(e)}")


def extract_grammar_rules(content: str, format: str) -> List[str]:
    """Extract rule names from grammar content."""
    rules = []
    
    try:
        if format == 'tgf':
            # Extract TGF rules (look for rule definitions)
            import re
            # Look for patterns like "rule_name ::=" or "rule_name :"
            pattern = r'^(\w+)\s*(?:::=|:)'
            for line in content.split('\n'):
                match = re.match(pattern, line.strip())
                if match:
                    rules.append(match.group(1))
                    
        elif format == 'ebnf':
            # Extract EBNF rules
            import re
            pattern = r'^(\w+)\s*='
            for line in content.split('\n'):
                match = re.match(pattern, line.strip())
                if match:
                    rules.append(match.group(1))
                    
        elif format == 'lark':
            # Extract Lark rules
            import re
            pattern = r'^(\w+)\s*:'
            for line in content.split('\n'):
                if not line.strip().startswith('//') and not line.strip().startswith('#'):
                    match = re.match(pattern, line.strip())
                    if match:
                        rules.append(match.group(1))
    except Exception:
        pass
    
    return rules


@router.post("/load-tau-grammar")
async def load_tau_grammar(request: Request, file: UploadFile = File(...)):
    """Load a user-provided Tau grammar file for translation."""
    try:
        # Validate file extension
        if not file.filename.endswith(('.lark', '.ebnf', '.tgf')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload a .lark, .ebnf, or .tgf file"
            )
        
        # Read file content
        content = await file.read()
        grammar_text = content.decode('utf-8')
        
        # Get the grammar engine from app state
        if not hasattr(request.app.state, 'grammar_engine'):
            raise HTTPException(
                status_code=503,
                detail="Grammar engine not available. Please enable grammar feature in settings."
            )
        
        grammar_engine = request.app.state.grammar_engine
        
        # Save grammar file temporarily
        temp_dir = settings.project_root / "temp" / "grammars"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = temp_dir / file.filename
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(grammar_text)
        
        # Load the grammar into the engine
        success = grammar_engine.load_tau_grammar(str(temp_file))
        
        if success:
            # Extract rules for metadata
            format = file.filename.split('.')[-1]
            rules = extract_grammar_rules(grammar_text, format)
            
            return create_success_response({
                "message": "Tau grammar loaded successfully",
                "filename": file.filename,
                "format": format,
                "rules_found": len(rules),
                "rules": rules[:20],  # First 20 rules
                "can_translate_to_tce": True
            })
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to load grammar. Please check the grammar syntax."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading Tau grammar: {e}")
        return create_error_response(f"Failed to load grammar: {str(e)}")


@router.get("/tau-grammar-status")
async def get_tau_grammar_status(request: Request):
    """Check if a Tau grammar is loaded and ready for translation."""
    try:
        if not hasattr(request.app.state, 'grammar_engine'):
            return create_success_response({
                "loaded": False,
                "message": "Grammar engine not available"
            })
        
        grammar_engine = request.app.state.grammar_engine
        
        # Check if Tau parser is loaded
        tau_loaded = grammar_engine.tau_parser is not None
        
        return create_success_response({
            "loaded": tau_loaded,
            "can_translate_to_tau": grammar_engine.tce_parser is not None,
            "can_translate_to_tce": tau_loaded,
            "message": "Tau grammar loaded" if tau_loaded else "No Tau grammar loaded"
        })
        
    except Exception as e:
        logger.error(f"Error checking grammar status: {e}")
        return create_error_response(f"Failed to check grammar status: {str(e)}")