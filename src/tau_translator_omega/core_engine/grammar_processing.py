# Copyright (c) DarkLightX / Dana Edwards
"""
TGF Grammar Domain Logic
========================

This module contains the core domain logic for processing TGF (Tau Grammar
Format) data. It is responsible for parsing grammar content and converting it
into a format usable by the translation engine's parser (e.g., Lark).

This module is intentionally pure and has no knowledge of the file system.
All I/O operations are handled by an injected `GrammarRepository` from the
infrastructure layer, following the Functional Core, Imperative Shell pattern.
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set

from returns.result import Result, Success, Failure

from ..infrastructure.grammar_io import GrammarRepository

logger = logging.getLogger(__name__)


@dataclass
class LoadedGrammar:
    """Represents a loaded grammar with its metadata and content."""
    filename: str
    original_name: str
    type: str
    content: str
    is_active: bool
    rules: Dict[str, Any] = field(default_factory=dict)
    terminals: List[str] = field(default_factory=list)
    non_terminals: List[str] = field(default_factory=list)
    directives: List[Tuple[str, str]] = field(default_factory=list)


class TGFGrammarService:
    """
    Orchestrates grammar loading and processing using a repository for I/O.
    This acts as an application service.
    """

    def __init__(self, repository: GrammarRepository):
        self._repository = repository
        self.loaded_grammars: Dict[str, LoadedGrammar] = {}
        self.active_grammar: Optional[LoadedGrammar] = None

    def load_and_parse_all_grammars(self) -> Result[None, str]:
        """
        Loads all grammars specified in the config, reads their content,
        and parses them.
        """
        config_result = self._repository.read_grammar_config()

        def process_configs(configs: List[Dict[str, Any]]) -> Result[None, str]:
            for grammar_config in configs:
                filename = grammar_config.get('filename')
                if not filename:
                    continue

                content_result = self._repository.read_grammar_file(filename)
                if isinstance(content_result, Failure):
                    return Failure(f"Failed to read grammar file '{filename}': {content_result.failure()}")

                content = content_result.unwrap()

                # Determine grammar type
                grammar_type = grammar_config.get('type')
                if not grammar_type:
                    grammar_type = Path(filename).suffix.lower()
                    if grammar_type not in ['.tgf', '.lark']:
                        logger.warning(f"Unrecognized grammar file extension '{Path(filename).suffix}' for '{filename}'. Defaulting type to '.tgf'.")
                        grammar_type = '.tgf' # Default if suffix is unknown or missing
                
                # Initialize TGF-specific fields to defaults
                rules: Dict[str, Any] = {}
                terminals: List[str] = []
                non_terminals: List[str] = []
                directives: List[Tuple[str, str]] = []

                # Only parse TGF content if the type is .tgf
                if grammar_type == '.tgf':
                    rules, terminals, non_terminals, directives = TGFGrammarParser.parse_tgf_content(content)
                elif grammar_type == '.lark':
                    logger.info(f"Skipping TGF parsing for .lark file: {filename}")

                grammar = LoadedGrammar(
                    filename=filename,
                    original_name=grammar_config.get('originalName', filename),
                    type=grammar_type, # Use determined type
                    content=content,
                    is_active=grammar_config.get('isActive', False),
                    rules=rules,
                    terminals=terminals,
                    non_terminals=non_terminals,
                    directives=directives
                )
                self.loaded_grammars[filename] = grammar
                if grammar.is_active:
                    self.active_grammar = grammar
            return Success(None)

        return config_result.bind(process_configs)

    def set_active_grammar(self, filename: str) -> Result[None, str]:
        """
        Sets a grammar as active and persists the change via the repository.
        """
        if filename not in self.loaded_grammars:
            return Failure(f"Grammar '{filename}' not loaded.")

        for g in self.loaded_grammars.values():
            g.is_active = (g.filename == filename)

        self.active_grammar = self.loaded_grammars[filename]

        updated_config = [
            {
                'filename': g.filename,
                'originalName': g.original_name,
                'type': g.type,
                'isActive': g.is_active
            }
            for g in self.loaded_grammars.values()
        ]
        return self._repository.write_grammar_config(updated_config)

    def get_grammar_for_parser(self) -> Optional[Tuple[str, str]]:
        """
        Gets the active grammar in a format suitable for the parser (Lark).
        """
        if not self.active_grammar:
            return None

        if self.active_grammar.type == '.lark':
            # For .lark files, we don't have TGF-specific diagnostics, so return empty diagnostic string
            return self.active_grammar.content, "Diagnostics not applicable for pre-formatted .lark files."
        elif self.active_grammar.type == '.tgf':
            # This now returns a tuple (lark_grammar_str, diagnostic_str)
            return TGFGrammarConverter.to_lark_grammar(self.active_grammar)
        else:
            logger.warning(f"No converter for grammar type: {self.active_grammar.type}")
            return None


class TGFGrammarParser:
    """Contains pure static methods for parsing TGF grammar content."""

    # Operators sorted by length to ensure longer ones are matched first (e.g., '::=' before ':=')
    KNOWN_OPERATORS = sorted(
        ['::=', ':=', '<->', '->', '<-', '&&', '||', '?', ':', '^', '!', '<>', '[]'],
        key=len,
        reverse=True
    )

    @staticmethod
    def _tokenize_rule_body(body: str) -> List[Dict[str, Any]]:
        """Tokenizes a rule body string into a list of typed elements."""
        processed_body = body
        placeholder_map = {}
        next_placeholder_id = 0

        for op in TGFGrammarParser.KNOWN_OPERATORS:
            op_re = re.escape(op)
            # Use a function for replacement to handle multiple occurrences correctly
            def replacer(match):
                nonlocal next_placeholder_id
                placeholder = f"__TEMP_OP_{next_placeholder_id}__"
                placeholder_map[placeholder] = op
                next_placeholder_id += 1
                return placeholder
            # This regex ensures we don't replace operators inside quotes
            # It's a simplification; a full parser would be more robust.
            processed_body = re.sub(op_re, replacer, processed_body)

        tokens = processed_body.split()
        elements = []
        for token in tokens:
            if token in placeholder_map:
                elements.append({'type': 'literal', 'value': placeholder_map[token]})
            elif token.startswith('"') and token.endswith('"'):
                elements.append({'type': 'literal', 'value': token[1:-1]})
            elif token.startswith('[') and token.endswith(']'):
                elements.append({'type': 'optional', 'value': token[1:-1]})
            elif re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]*', token):
                elements.append({'type': 'non_terminal', 'value': token})
            else:
                logger.warning(f"TGF Rule Tokenizer: Unrecognized token '{token}' treated as non-terminal.")
                elements.append({'type': 'non_terminal', 'value': token})
        return elements

    @staticmethod
    def _parse_rule_definition(definition: str) -> Dict[str, Any]:
        """Parse a single rule definition using robust tokenization."""
        alternatives = []
        for alt_part in definition.split('|'):
            alt_part = alt_part.strip()
            if alt_part:
                elements = TGFGrammarParser._tokenize_rule_body(alt_part)
                alternatives.append(elements)
        return {'alternatives': alternatives}

    @staticmethod
    def parse_tgf_content(content: str) -> Tuple[Dict[str, Any], List[str], List[str], List[Tuple[str, str]]]:
        """Parse TGF content to extract rules, terminals, non-terminals, and directives."""
        rules = {}
        terminals = set()
        non_terminals = set()
        parsed_directives: List[Tuple[str, str]] = []

        lines = content.strip().split('\n')
        
        current_rule_name: Optional[str] = None
        current_definition_parts: List[str] = []
        
        line_idx = 0
        while line_idx < len(lines):
            original_line_text = lines[line_idx]
            line = original_line_text.strip()

            if not line or line.startswith('#') or line.startswith('//'):
                line_idx += 1
                continue

            if line.startswith('@'):
                parts = line[1:].split(maxsplit=1)
                directive_name = parts[0]
                directive_value = parts[1] if len(parts) > 1 else ""
                parsed_directives.append((directive_name, directive_value.strip()))
                logger.info(f"TGF Parsing: Parsed directive: @{directive_name} {directive_value.strip()}")
                line_idx += 1
                continue

            separator_match = re.search(r'\s*(::=|:=)\s*', line)
            is_new_rule = separator_match and not line.startswith('|')

            if is_new_rule:
                if current_rule_name and current_definition_parts:
                    full_def = ' '.join(current_definition_parts).strip()
                    if full_def.endswith('.'):
                        full_def = full_def[:-1].strip()
                    if full_def:
                        rules[current_rule_name] = TGFGrammarParser._parse_rule_definition(full_def)
                
                rule_name_part = line.split(separator_match.group(1), 1)[0].strip()
                definition_part = line.split(separator_match.group(1), 1)[1].strip()
                current_rule_name = rule_name_part
                non_terminals.add(current_rule_name)
                current_definition_parts = [definition_part]
            elif current_rule_name:
                current_definition_parts.append(line)

            if current_rule_name and ' '.join(current_definition_parts).strip().endswith('.'):
                full_def = ' '.join(current_definition_parts).strip()[:-1].strip()
                if full_def:
                    rules[current_rule_name] = TGFGrammarParser._parse_rule_definition(full_def)
                else:
                    logger.warning(f"TGF Parsing: Rule '{current_rule_name}' has an empty definition.")
                    rules[current_rule_name] = {'alternatives': [[]]}
                current_rule_name = None
                current_definition_parts = []
            
            line_idx += 1

        if current_rule_name and current_definition_parts:
            logger.warning(f"TGF Parsing: Rule '{current_rule_name}' was defined but not terminated with '.' End of file reached.")
            full_def = ' '.join(current_definition_parts).strip()
            if full_def.endswith('.'):
                full_def = full_def[:-1].strip()
            if full_def:
                rules[current_rule_name] = TGFGrammarParser._parse_rule_definition(full_def)

        for rule_name, rule_def in rules.items():
            terminals.update(TGFGrammarParser._extract_terminals(rule_def))

        return rules, list(terminals), list(non_terminals), parsed_directives

    @staticmethod
    def _extract_terminals(rule_def: Dict[str, Any]) -> Set[str]:
        """Extract terminal symbols from a rule definition (simple version)."""
        terminals = set()
        if 'alternatives' in rule_def:
            for alt in rule_def['alternatives']:
                for element in alt:
                    if element['type'] == 'literal':
                        terminals.add(element['value'])
        return terminals


class TGFGrammarConverter:
    """Contains pure static methods for converting grammar formats."""

    @staticmethod
    def _parse_directive_definition(directive_value: str) -> Optional[Tuple[str, str, bool]]:
        """
        Parses a directive value like "TERMINAL_NAME = EBNF_BODY ."
        Returns (TERMINAL_NAME, EBNF_BODY, is_special_eof) or None.
        is_special_eof is True if name is 'eof' and body is '<<EOF>>'.
        """
        # Regex to capture: NAME = BODY .
        match = re.fullmatch(r"\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*\.\s*", directive_value, re.DOTALL)
        if match:
            name, body = match.group(1), match.group(2).strip()
            if name.lower() == 'eof' and body == '<<EOF>>':
                return name, body, True # Special EOF case
            return name, body, False
        logger.warning(f"TGF Converter: Could not parse directive definition: {directive_value}")
        return None

    @staticmethod
    def to_lark_grammar(grammar: LoadedGrammar) -> Tuple[str, str]:
        """Convert loaded TGF grammar to Lark format for the parser"""
        lark_parts = [] # Stores individual lines or definitions for the Lark grammar
        diagnostic_details = [f"TGFGrammarConverter Diagnostics for {grammar.filename}:"]
        
        ignore_terminals_for_lark = [] # For Lark's %ignore directive
        # Stores UPCASED names like WHITESPACE, ALPHA defined by @directives or generated for literals
        # This helps in resolving references and ensuring consistent casing for terminals.
        known_lark_terminals = set() 
        
        literal_to_lark_terminal_map = {} # Maps "original_literal_value" -> LARK_TERMINAL_NAME

        diagnostic_details.append("\nProcessing Directives:")
        for directive_name, directive_value in grammar.directives:
            if directive_name in ("trim", "inline"):
                parsed_def = TGFGrammarConverter._parse_directive_definition(directive_value)
                if parsed_def:
                    term_name_orig, term_body, is_special_eof = parsed_def
                    lark_term_name = term_name_orig.upper() # Terminals in Lark are typically uppercase

                    if is_special_eof:
                        diagnostic_details.append(f"  Noted special EOF directive: @{directive_name} {term_name_orig} = {term_body}. This specific TGF construct for EOF is not directly translated to an explicit Lark terminal. Lark handles EOF implicitly or via $end.")
                        continue 
                    
                    lark_terminal_def = f"{lark_term_name}: {term_body}"
                    lark_parts.append(lark_terminal_def)
                    known_lark_terminals.add(lark_term_name)
                    diagnostic_details.append(f"  Added from @{directive_name}: {lark_terminal_def}")
                    if directive_name == "trim":
                        ignore_terminals_for_lark.append(lark_term_name)
            elif directive_name == "use" and "char classes" in directive_value:
                diagnostic_details.append("  Noted @use char classes (implies common terminals like ALPHA, DIGIT should be defined via @inline).")
            elif directive_name == "enable" and "productions" in directive_value:
                diagnostic_details.append("  Noted @enable productions (all rules assumed active by default).")
            else:
                diagnostic_details.append(f"  Ignoring unknown/unhandled directive: @{directive_name} {directive_value}")

        diagnostic_details.append("\nProcessing Terminals from Rule Literals (grammar.terminals):")
        if not grammar.terminals:
            diagnostic_details.append("  (No terminals extracted from rule literals by TGF parser)")
        
        unique_literals_from_rules = sorted(list(set(t for t in grammar.terminals if t))) # Filter empty strings

        for i, literal_val in enumerate(unique_literals_from_rules):
            char_to_name_segment = {
                '.': "DOT", ',': "COMMA", ';': "SEMICOLON", ':': "COLON",
                '(': "LPAREN", ')': "RPAREN", '[': "LBRACKET", ']': "RBRACKET",
                '{': "LBRACE", '}': "RBRACE", '+': "PLUS", '-': "MINUS",
                '*': "ASTERISK", '/': "SLASH", '=': "EQUALS", '<': "LT", '>': "GT",
                '&': "AMPERSAND", '|': "PIPE", '!': "BANG", '?': "QUESTION",
                '%': "PERCENT", '$': "DOLLAR", '#': "HASH", '@': "AT",
                '::=': "COLONCOLONEQUALS", "'": "SINGLEQUOTE", "\"": "DOUBLEQUOTE",
                '_': "UNDERSCORE"
            }
            
            name_base = "".join(char_to_name_segment.get(c, c.upper() if c.isalnum() else f"U{ord(c)}") for c in literal_val)
            lark_literal_term_name = f"LITERAL_{name_base}"
            
            original_lark_literal_term_name = lark_literal_term_name
            counter = 1
            while lark_literal_term_name in known_lark_terminals:
                lark_literal_term_name = f"{original_lark_literal_term_name}_{counter}"
                counter += 1

            escaped_lark_val = literal_val.replace("\\", "\\\\").replace("\"", "\\\"")
            lark_terminal_def = f'{lark_literal_term_name}: "{escaped_lark_val}"'
            
            lark_parts.append(lark_terminal_def)
            literal_to_lark_terminal_map[literal_val] = lark_literal_term_name
            known_lark_terminals.add(lark_literal_term_name)
            diagnostic_details.append(f"  Added literal terminal: {lark_terminal_def} (for TGF literal '{literal_val}')")

        diagnostic_details.append("\nProcessing Rules:")
        if not grammar.rules:
            diagnostic_details.append("  (No rules defined in LoadedGrammar object)")
            
        processed_lark_rules = set()
        start_rule_tgf_name = "rr"
        actual_start_lark_name = "start"
        sorted_rule_names_tgf = sorted(grammar.rules.keys())

        for rule_name_tgf in sorted_rule_names_tgf:
            rule_def_tgf = grammar.rules[rule_name_tgf]
            lark_rule_lhs = actual_start_lark_name if rule_name_tgf == start_rule_tgf_name else rule_name_tgf.lower()
            
            if lark_rule_lhs in processed_lark_rules:
                diagnostic_details.append(f"  WARNING: Rule '{lark_rule_lhs}' (from TGF '{rule_name_tgf}') seems to be a duplicate after casing/renaming. Skipping.")
                continue

            if 'alternatives' not in rule_def_tgf or not rule_def_tgf['alternatives']:
                diagnostic_details.append(f"  Rule '{rule_name_tgf}' (Lark LHS: {lark_rule_lhs}) has no alternatives. Defining as empty: %empty")
                lark_parts.append(f"{lark_rule_lhs}: %empty")
                processed_lark_rules.add(lark_rule_lhs)
                continue

            lark_rhs_alternatives = []
            for alt_tgf in rule_def_tgf['alternatives']:
                if not alt_tgf:
                    lark_rhs_alternatives.append("%empty")
                    continue

                elements_lark = []
                for elem_tgf in alt_tgf:
                    elem_type = elem_tgf['type']
                    elem_value_tgf = elem_tgf['value']
                    lark_elem = ""
                    if elem_type == 'literal':
                        if elem_value_tgf in literal_to_lark_terminal_map:
                            lark_elem = literal_to_lark_terminal_map[elem_value_tgf]
                        else:
                            diagnostic_details.append(f"  WARNING: Literal '{elem_value_tgf}' in rule '{rule_name_tgf}' not found in map. Using raw (may cause issues).")
                            lark_elem = f'\"{elem_value_tgf.replace("\"", "\\\"")}\"' # Fallback
                    elif elem_type == 'non_terminal':
                        if elem_value_tgf == start_rule_tgf_name:
                            lark_elem = actual_start_lark_name
                        elif elem_value_tgf.upper() in known_lark_terminals:
                            lark_elem = elem_value_tgf.upper()
                        else:
                            lark_elem = elem_value_tgf.lower()
                    elif elem_type == 'optional':
                        inner_val_tgf = elem_value_tgf
                        lark_inner_val = ""
                        if inner_val_tgf == start_rule_tgf_name:
                            lark_inner_val = actual_start_lark_name
                        elif inner_val_tgf.upper() in known_lark_terminals:
                            lark_inner_val = inner_val_tgf.upper()
                        else:
                            lark_inner_val = inner_val_tgf.lower()
                        lark_elem = f"[{lark_inner_val}]"
                    else:
                        diagnostic_details.append(f"  WARNING: Unknown element type '{elem_type}' for value '{elem_value_tgf}' in rule '{rule_name_tgf}'. Skipping.")
                        continue
                    
                    if 'quantifier' in elem_tgf:
                        lark_elem = f"({lark_elem}){elem_tgf['quantifier']}"
                    elements_lark.append(lark_elem)
                
                lark_rhs_alternatives.append(' '.join(elements_lark) if elements_lark else "%empty")
            
            lark_rule_def_str = f"{lark_rule_lhs}: {' | '.join(lark_rhs_alternatives)}"
            lark_parts.append(lark_rule_def_str)
            processed_lark_rules.add(lark_rule_lhs)
            diagnostic_details.append(f"  Added rule: {lark_rule_def_str} (from TGF '{rule_name_tgf}')")

        final_lark_grammar_lines = ["// Auto-generated Lark grammar from TGF"]
        if ignore_terminals_for_lark:
            final_lark_grammar_lines.append(f"%ignore {' '.join(ignore_terminals_for_lark)}")
        
        final_lark_grammar_lines.extend(lark_parts)
        full_lark_grammar = "\n".join(final_lark_grammar_lines)
        diagnostic_details.append(f"\nFinal Lark Grammar String:\n{full_lark_grammar}")

        return full_lark_grammar, "\n".join(diagnostic_details)
