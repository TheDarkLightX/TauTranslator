"""
TGF service with pure business logic following the Intentional Disclosure Principle.

Contains all TGF grammar loading and parsing business logic separated from infrastructure concerns.
All methods follow IDP Rule 2 (≤10 lines) and Rule 3 (type disclosure).

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, List, Optional, Tuple
from returns.result import Result, Success, Failure

from .tgf_types import (
    TGFFilename, TGFContent, TGFRuleName, TerminalSymbol, NonTerminalSymbol,
    RuleElement, GrammarRule, ParsedTGFGrammar, LoadedGrammar, GrammarConfig,
    GrammarLoaderConfig, LarkConversionResult, GrammarLoadingState, TGFParseError,
    ElementType, QuantifierType, GrammarFileType, LarkGrammar
)
from ..infrastructure.tgf_infrastructure import (
    ConfigFileManager, GrammarFileReader, DirectoryValidator,
    GrammarFileTypeDetector, LoadedGrammarFactory, TGFFileScanner
)


class TGFParsingService:
    """Pure business logic for TGF grammar parsing."""
    
    def parse_tgf_content(self, content: TGFContent) -> Result[ParsedTGFGrammar, TGFParseError]:
        """Parse TGF content into structured grammar representation."""
        try:
            rules_dict = {}
            terminals_set = set()
            non_terminals_set = set()
            
            # Parse rules from content
            parse_result = self._extract_rules_from_content(str(content))
            if isinstance(parse_result, Failure):
                return parse_result
            
            raw_rules = parse_result.unwrap()
            
            # Convert raw rules to structured format
            for rule_name, rule_definition in raw_rules.items():
                rule = self._create_grammar_rule(rule_name, rule_definition)
                rules_dict[rule_name] = rule
                non_terminals_set.add(NonTerminalSymbol(rule_name))
                terminals_set.update(rule.get_terminals())
            
            return Success(ParsedTGFGrammar(
                rules=rules_dict,
                terminals=list(terminals_set),
                non_terminals=list(non_terminals_set)
            ))
            
        except Exception as e:
            return Failure(TGFParseError(
                line_number=None,
                error_message=f"Failed to parse TGF content: {e}"
            ))
    
    def _extract_rules_from_content(self, content: str) -> Result[Dict[str, str], TGFParseError]:
        """Extract raw rule definitions from TGF content."""
        lines = content.strip().split('\n')
        rules = {}
        current_rule = None
        current_definition = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments and empty lines
            if self._should_skip_line(line):
                continue
            
            # Process rule line
            result = self._process_rule_line(line, current_rule, current_definition, rules)
            if isinstance(result, Failure):
                error = result.failure()
                error.line_number = line_num
                return Failure(error)
            
            current_rule, current_definition = result.unwrap()
        
        return Success(rules)
    
    def _should_skip_line(self, line: str) -> bool:
        """Check if line should be skipped during parsing."""
        return not line or line.startswith('#') or line.startswith('//')
    
    def _process_rule_line(self, line: str, current_rule: Optional[str], 
                          current_definition: List[str], rules: Dict[str, str]
                          ) -> Result[Tuple[Optional[str], List[str]], TGFParseError]:
        """Process a single line for rule extraction."""
        # End of rule
        if line.endswith('.'):
            if current_rule:
                definition = ' '.join(current_definition) + ' ' + line[:-1]
                rules[current_rule] = definition
            return Success((None, []))
        
        # Start of new rule
        if self._is_rule_start(line) and not current_rule:
            return self._handle_rule_start(line)
        
        # Continuation of current rule
        if current_rule:
            current_definition.append(line)
            return Success((current_rule, current_definition))
        
        return Failure(TGFParseError(
            line_number=None,
            error_message=f"Unexpected line format: {line}"
        ))
    
    def _is_rule_start(self, line: str) -> bool:
        """Check if line starts a new rule definition."""
        return '::=' in line or ('=' in line and '==' not in line)
    
    def _handle_rule_start(self, line: str) -> Result[Tuple[str, List[str]], TGFParseError]:
        """Handle the start of a new rule definition."""
        if '::=' in line:
            parts = line.split('::=', 1)
        else:
            parts = line.split('=', 1)
        
        rule_name = parts[0].strip()
        remaining = parts[1].strip() if len(parts) > 1 else ""
        
        if remaining.endswith('.'):
            # Complete rule on one line - will be handled by caller
            return Success((rule_name, [remaining[:-1]]))
        else:
            return Success((rule_name, [remaining] if remaining else []))
    
    def _create_grammar_rule(self, rule_name: str, definition: str) -> GrammarRule:
        """Create structured grammar rule from definition string."""
        alternatives = []
        
        # Split by | for alternatives
        alt_parts = definition.split('|')
        
        for alt in alt_parts:
            alt = alt.strip()
            if alt:
                elements = self._parse_alternative_elements(alt)
                alternatives.append(elements)
        
        return GrammarRule(
            name=TGFRuleName(rule_name),
            alternatives=alternatives
        )
    
    def _parse_alternative_elements(self, alternative: str) -> List[RuleElement]:
        """Parse elements within a rule alternative."""
        elements = []
        tokens = alternative.split()
        
        for token in tokens:
            element = self._parse_single_token(token)
            if element:
                elements.append(element)
        
        return elements
    
    def _parse_single_token(self, token: str) -> Optional[RuleElement]:
        """Parse a single token into a rule element."""
        # String literal
        if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
            return RuleElement.create_literal(token[1:-1])
        
        # Quantifier
        if token in ['?', '*', '+']:
            return None  # Handled by previous element
        
        # Optional element
        if token.startswith('[') and token.endswith(']'):
            return RuleElement.create_optional(token[1:-1])
        
        # Non-terminal reference
        return RuleElement.create_non_terminal(token)


class LarkConversionService:
    """Converts TGF grammars to Lark format."""
    
    def convert_to_lark(self, grammar: LoadedGrammar) -> LarkConversionResult:
        """Convert loaded grammar to Lark format."""
        if grammar.file_type == GrammarFileType.LARK:
            return LarkConversionResult.success_result(
                str(grammar.content), 0, 0
            )
        
        if not grammar.parsed_grammar:
            return LarkConversionResult.failure_result(
                "Grammar must be parsed before conversion"
            )
        
        try:
            lark_content = self._build_lark_grammar(grammar.parsed_grammar)
            return LarkConversionResult.success_result(
                lark_content,
                grammar.parsed_grammar.terminal_count,
                grammar.parsed_grammar.rule_count
            )
        except Exception as e:
            return LarkConversionResult.failure_result(f"Conversion failed: {e}")
    
    def _build_lark_grammar(self, parsed_grammar: ParsedTGFGrammar) -> str:
        """Build Lark grammar string from parsed TGF grammar."""
        lark_rules = []
        
        # Add header
        lark_rules.append("// Auto-generated from TGF grammar")
        lark_rules.append("%import common.WS")
        lark_rules.append("%ignore WS")
        lark_rules.append("")
        
        # Convert rules
        for rule in parsed_grammar.rules.values():
            lark_rule = self._convert_rule_to_lark(rule)
            lark_rules.append(lark_rule)
        
        return '\n'.join(lark_rules)
    
    def _convert_rule_to_lark(self, rule: GrammarRule) -> str:
        """Convert single rule to Lark format."""
        alternatives = []
        
        for alt in rule.alternatives:
            elements = []
            for elem in alt:
                lark_element = self._convert_element_to_lark(elem)
                elements.append(lark_element)
            alternatives.append(' '.join(elements))
        
        rule_name = str(rule.name).lower()
        return f"{rule_name}: {' | '.join(alternatives)}"
    
    def _convert_element_to_lark(self, element: RuleElement) -> str:
        """Convert rule element to Lark format."""
        if element.element_type == ElementType.LITERAL:
            result = f'"{element.value}"'
        elif element.element_type == ElementType.NON_TERMINAL:
            result = element.value.lower()
        elif element.element_type == ElementType.OPTIONAL:
            result = f"({element.value})?"
        else:
            result = element.value
        
        # Add quantifier if present
        if element.quantifier:
            result += element.quantifier.value
        
        return result


class GrammarManagementService:
    """Manages grammar loading, activation, and state."""
    
    def __init__(self, config: GrammarLoaderConfig):
        self._config = config
        self._parsing_service = TGFParsingService()
        self._conversion_service = LarkConversionService()
    
    def load_single_grammar(self, filename: TGFFilename) -> Result[LoadedGrammar, str]:
        """Load a single grammar file."""
        # Read file content
        content_result = GrammarFileReader.read_grammar_file(
            self._config.grammar_directory, filename
        )
        if isinstance(content_result, Failure):
            return Failure(content_result.failure())
        
        content = content_result.unwrap()
        grammar = LoadedGrammarFactory.create_loaded_grammar(filename, content)
        
        # Parse if TGF format
        if grammar.file_type == GrammarFileType.TGF:
            parse_result = self._parsing_service.parse_tgf_content(content)
            if isinstance(parse_result, Success):
                grammar = grammar.with_parsed_grammar(parse_result.unwrap())
        
        return Success(grammar)
    
    def create_loading_state(self, grammars: Dict[str, LoadedGrammar]) -> GrammarLoadingState:
        """Create current loading state from grammars."""
        active_grammar = None
        for grammar in grammars.values():
            if grammar.is_active:
                active_grammar = grammar
                break
        
        return GrammarLoadingState(
            loaded_grammars=grammars,
            active_grammar=active_grammar,
            total_loaded=len(grammars)
        )
    
    def activate_grammar(self, grammars: Dict[str, LoadedGrammar], 
                        filename: TGFFilename) -> Result[Dict[str, LoadedGrammar], str]:
        """Activate a specific grammar and deactivate others."""
        if str(filename) not in grammars:
            return Failure(f"Grammar not found: {filename}")
        
        # Update all grammars
        updated_grammars = {}
        for name, grammar in grammars.items():
            is_active = (name == str(filename))
            updated_grammars[name] = grammar.with_active_status(is_active)
        
        return Success(updated_grammars)
    
    def get_active_grammar_for_parser(self, state: GrammarLoadingState) -> Result[LarkGrammar, str]:
        """Get active grammar in Lark format for parser use."""
        if not state.has_active_grammar:
            return Failure("No active grammar selected")
        
        conversion_result = self._conversion_service.convert_to_lark(state.active_grammar)
        if not conversion_result.success:
            return Failure(conversion_result.error_message)
        
        return Success(conversion_result.lark_grammar)


class ConfigManagementService:
    """Manages grammar configuration persistence."""
    
    def __init__(self, config: GrammarLoaderConfig):
        self._config = config
    
    def load_grammar_configs(self) -> Result[List[GrammarConfig], str]:
        """Load grammar configurations from file."""
        result = ConfigFileManager.load_config(self._config.config_file_path)
        if isinstance(result, Failure):
            return Failure(result.failure())
        
        return Success(result.unwrap())
    
    def save_grammar_state(self, state: GrammarLoadingState) -> Result[None, str]:
        """Save current grammar state to configuration."""
        configs = []
        for grammar in state.loaded_grammars.values():
            config = GrammarConfig(
                filename=grammar.filename,
                original_name=grammar.original_name,
                file_type=grammar.file_type.value,
                is_active=grammar.is_active
            )
            configs.append(config)
        
        return ConfigFileManager.save_config(self._config.config_file_path, configs)