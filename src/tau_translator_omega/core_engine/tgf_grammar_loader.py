#!/usr/bin/env python3
"""
TGF Grammar Loader
==================

This module loads TGF (Tau Grammar Format) files and integrates them
with the translation engine. It bridges the gap between the UI's grammar
selection and the actual parsing/translation process.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class LoadedGrammar:
    """Represents a loaded grammar with its metadata and content"""
    filename: str
    original_name: str
    type: str
    content: str
    is_active: bool
    rules: Dict[str, Any]
    terminals: List[str]
    non_terminals: List[str]


class TGFGrammarLoader:
    """Loads and manages TGF grammar files for the translation engine"""
    
    def __init__(self, grammar_dir: Path = None, config_file: Path = None):
        self.grammar_dir = grammar_dir or Path("grammars")
        self.config_file = config_file or Path("config/grammar-files.json")
        self.loaded_grammars: Dict[str, LoadedGrammar] = {}
        self.active_grammar: Optional[LoadedGrammar] = None
        
    def load_grammar_config(self) -> List[Dict[str, Any]]:
        """Load the grammar configuration file"""
        if not self.config_file.exists():
            logger.warning(f"Grammar config file not found: {self.config_file}")
            return []
            
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading grammar config: {e}")
            return []
    
    def parse_tgf_content(self, content: str) -> Tuple[Dict[str, Any], List[str], List[str]]:
        """Parse TGF content to extract rules, terminals, and non-terminals"""
        rules = {}
        terminals = set()
        non_terminals = set()
        
        lines = content.strip().split('\n')
        current_rule = None
        current_definition = []
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#') or line.startswith('//'):
                continue
                
            # Handle rule definitions
            if line.endswith('.'):
                # End of rule
                if current_rule:
                    definition = ' '.join(current_definition) + ' ' + line[:-1]
                    rules[current_rule] = self._parse_rule_definition(definition)
                current_rule = None
                current_definition = []
            elif '::=' in line or '=' in line and not current_rule:
                # Start of new rule
                if '::=' in line:
                    parts = line.split('::=', 1)
                else:
                    parts = line.split('=', 1)
                    
                current_rule = parts[0].strip()
                non_terminals.add(current_rule)
                
                # Check if definition continues on same line
                if len(parts) > 1:
                    remaining = parts[1].strip()
                    if remaining.endswith('.'):
                        # Complete rule on one line
                        rules[current_rule] = self._parse_rule_definition(remaining[:-1])
                        current_rule = None
                    else:
                        current_definition = [remaining]
            elif current_rule:
                # Continuation of current rule
                current_definition.append(line)
        
        # Extract terminals from rules
        for rule_name, rule_def in rules.items():
            terminals.update(self._extract_terminals(rule_def))
            
        return rules, list(terminals), list(non_terminals)
    
    def _parse_rule_definition(self, definition: str) -> Dict[str, Any]:
        """Parse a single rule definition"""
        # This is a simplified parser - real implementation would be more complex
        alternatives = []
        
        # Split by | for alternatives
        alt_parts = definition.split('|')
        
        for alt in alt_parts:
            alt = alt.strip()
            if alt:
                # Parse each alternative
                elements = []
                tokens = alt.split()
                
                for token in tokens:
                    if token.startswith('"') and token.endswith('"'):
                        # String literal
                        elements.append({'type': 'literal', 'value': token[1:-1]})
                    elif token.startswith("'") and token.endswith("'"):
                        # Character literal
                        elements.append({'type': 'literal', 'value': token[1:-1]})
                    elif token in ['?', '*', '+']:
                        # Quantifier
                        if elements:
                            elements[-1]['quantifier'] = token
                    elif token.startswith('[') and token.endswith(']'):
                        # Optional
                        elements.append({'type': 'optional', 'value': token[1:-1]})
                    else:
                        # Non-terminal reference
                        elements.append({'type': 'non_terminal', 'value': token})
                        
                alternatives.append(elements)
                
        return {
            'type': 'rule',
            'alternatives': alternatives
        }
    
    def _extract_terminals(self, rule_def: Dict[str, Any]) -> List[str]:
        """Extract terminal symbols from a rule definition"""
        terminals = []
        
        if 'alternatives' in rule_def:
            for alt in rule_def['alternatives']:
                for element in alt:
                    if element.get('type') == 'literal':
                        terminals.append(element['value'])
                        
        return terminals
    
    def load_grammar_file(self, filename: str) -> Optional[LoadedGrammar]:
        """Load a specific grammar file"""
        filepath = self.grammar_dir / filename
        
        if not filepath.exists():
            logger.error(f"Grammar file not found: {filepath}")
            return None
            
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Parse based on file type
            if filename.endswith('.tgf'):
                rules, terminals, non_terminals = self.parse_tgf_content(content)
            else:
                # For other formats, just store content
                rules, terminals, non_terminals = {}, [], []
                
            grammar = LoadedGrammar(
                filename=filename,
                original_name=filename,
                type=filepath.suffix,
                content=content,
                is_active=False,
                rules=rules,
                terminals=terminals,
                non_terminals=non_terminals
            )
            
            self.loaded_grammars[filename] = grammar
            logger.info(f"Loaded grammar: {filename} ({len(rules)} rules)")
            return grammar
            
        except Exception as e:
            logger.error(f"Error loading grammar {filename}: {e}")
            return None
    
    def load_all_grammars(self) -> int:
        """Load all grammar files from config"""
        config = self.load_grammar_config()
        loaded_count = 0
        
        for grammar_info in config:
            filename = grammar_info.get('filename')
            if filename:
                grammar = self.load_grammar_file(filename)
                if grammar:
                    grammar.is_active = grammar_info.get('isActive', False)
                    if grammar.is_active:
                        self.active_grammar = grammar
                    loaded_count += 1
                    
        logger.info(f"Loaded {loaded_count} grammar files")
        return loaded_count
    
    def get_active_grammar(self) -> Optional[LoadedGrammar]:
        """Get the currently active grammar"""
        return self.active_grammar
    
    def set_active_grammar(self, filename: str) -> bool:
        """Set a grammar as active"""
        if filename in self.loaded_grammars:
            # Deactivate all grammars
            for g in self.loaded_grammars.values():
                g.is_active = False
                
            # Activate selected grammar
            self.loaded_grammars[filename].is_active = True
            self.active_grammar = self.loaded_grammars[filename]
            
            # Update config file
            self._update_config()
            return True
            
        return False
    
    def _update_config(self):
        """Update the configuration file with current active status"""
        config = []
        
        for grammar in self.loaded_grammars.values():
            config.append({
                'filename': grammar.filename,
                'originalName': grammar.original_name,
                'type': grammar.type,
                'isActive': grammar.is_active
            })
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Error updating config: {e}")
    
    def convert_to_lark_grammar(self, grammar: LoadedGrammar) -> str:
        """Convert loaded TGF grammar to Lark format for the parser"""
        lark_rules = []
        
        # Add terminals
        for terminal in grammar.terminals:
            # Escape special characters
            escaped = terminal.replace('"', '\\"')
            lark_rules.append(f'TERMINAL_{terminal.upper()}: "{escaped}"')
        
        # Convert rules
        for rule_name, rule_def in grammar.rules.items():
            if 'alternatives' in rule_def:
                alt_strings = []
                
                for alt in rule_def['alternatives']:
                    elements = []
                    for elem in alt:
                        if elem['type'] == 'literal':
                            elements.append(f'"{elem["value"]}"')
                        elif elem['type'] == 'non_terminal':
                            elements.append(elem['value'].lower())
                        elif elem['type'] == 'optional':
                            elements.append(f"({elem['value']})?")
                            
                        # Handle quantifiers
                        if 'quantifier' in elem:
                            elements[-1] += elem['quantifier']
                            
                    alt_strings.append(' '.join(elements))
                
                # Create Lark rule
                lark_rule = f"{rule_name.lower()}: {' | '.join(alt_strings)}"
                lark_rules.append(lark_rule)
        
        # Add standard imports
        lark_grammar = """// Auto-generated from TGF grammar
%import common.WS
%ignore WS

"""
        lark_grammar += '\n'.join(lark_rules)
        
        return lark_grammar
    
    def get_grammar_for_parser(self) -> Optional[str]:
        """Get the active grammar in a format suitable for the parser"""
        if not self.active_grammar:
            return None
            
        if self.active_grammar.type == '.lark':
            # Already in Lark format
            return self.active_grammar.content
        elif self.active_grammar.type == '.tgf':
            # Convert TGF to Lark
            return self.convert_to_lark_grammar(self.active_grammar)
        else:
            # Other formats need custom conversion
            logger.warning(f"No converter for grammar type: {self.active_grammar.type}")
            return None


# Global instance for easy access
_grammar_loader = None

def get_grammar_loader() -> TGFGrammarLoader:
    """Get or create the global grammar loader instance"""
    global _grammar_loader
    if _grammar_loader is None:
        _grammar_loader = TGFGrammarLoader()
        _grammar_loader.load_all_grammars()
    return _grammar_loader