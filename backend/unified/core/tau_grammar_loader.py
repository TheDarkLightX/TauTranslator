"""
Tau Grammar Loader
==================

Shared utility for loading Tau grammar files for both parser and LLM.
This ensures both systems use the same grammar specification.

Copyright: DarkLightX/Dana Edwards
"""

from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class TauGrammarLoader:
    """Centralized loader for Tau grammar files."""
    
    # Known grammar file locations
    GRAMMAR_PATHS = [
        ('tau_controlled', 'src/tau_translator_omega/core_engine/parsers/grammars/tau_controlled.lark'),
        ('tau_official', 'backend/tau.tgf'),
        ('tau_docs', 'docs/tau.tgf'),
        ('tau_enhanced', 'src/tau_translator_omega/core_engine/parsers/grammars/tau_enhanced_compliant.lark'),
    ]
    
    @classmethod
    def find_grammar_file(cls, preferred: Optional[str] = None) -> Optional[Path]:
        """Find the first available grammar file (≤10 lines)."""
        project_root = Path(__file__).parent.parent.parent.parent
        
        # Try preferred grammar first if specified
        if preferred:
            for name, rel_path in cls.GRAMMAR_PATHS:
                if name == preferred:
                    path = project_root / rel_path
                    if path.exists():
                        return path
        
        # Try all paths
        for name, rel_path in cls.GRAMMAR_PATHS:
            path = project_root / rel_path
            if path.exists():
                return path
                
        return None
    
    @classmethod
    def load_grammar(cls, preferred: Optional[str] = None) -> Tuple[Optional[str], Optional[Path]]:
        """Load grammar content and return with path (≤10 lines)."""
        grammar_path = cls.find_grammar_file(preferred)
        
        if not grammar_path:
            logger.warning("No Tau grammar file found")
            return None, None
            
        try:
            content = grammar_path.read_text(encoding='utf-8')
            logger.info(f"Loaded Tau grammar from {grammar_path}")
            return content, grammar_path
        except Exception as e:
            logger.error(f"Failed to load grammar from {grammar_path}: {e}")
            return None, None
    
    @classmethod
    def get_grammar_info(cls) -> Dict[str, Any]:
        """Get information about available grammars (≤10 lines)."""
        project_root = Path(__file__).parent.parent.parent.parent
        info = {
            'available': [],
            'missing': [],
            'preferred': None
        }
        
        for name, rel_path in cls.GRAMMAR_PATHS:
            path = project_root / rel_path
            if path.exists():
                info['available'].append({
                    'name': name,
                    'path': str(path),
                    'size': path.stat().st_size
                })
                if not info['preferred']:
                    info['preferred'] = name
            else:
                info['missing'].append({'name': name, 'expected_path': str(path)})
                
        return info
    
    @classmethod
    def extract_grammar_rules(cls, grammar_content: str) -> Dict[str, str]:
        """Extract key grammar rules for quick reference (≤10 lines)."""
        rules = {}
        current_rule = None
        
        for line in grammar_content.split('\n'):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('//') or line.startswith('%'):
                continue
                
            # New rule definition
            if ':' in line and not line.startswith(' '):
                parts = line.split(':', 1)
                current_rule = parts[0].strip()
                rules[current_rule] = line
            elif current_rule and line:
                # Continuation of previous rule
                rules[current_rule] += '\n    ' + line
                
        return rules