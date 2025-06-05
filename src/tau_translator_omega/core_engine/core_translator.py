"""
Core TCE to TAU Translator
==========================

Core implementation for TCE to TAU translation with BDD testing support.
"""

from typing import Optional, Dict, Any


class CoreParser:
    """Core parser for TCE and TAU input."""
    
    def parse(self, text: str, language: str = 'TCE') -> 'SimpleAST':
        """Parse TCE or TAU text into AST."""
        if not text:
            raise ValueError("Input cannot be empty")
        
        if language == 'TCE' and not text.strip().endswith('.'):
            raise SyntaxError("TCE input must end with period")
        
        return CoreAST(text, language)


class CoreAST:
    """Core Abstract Syntax Tree representation."""
    
    def __init__(self, text: str, language: str):
        self.text = text
        self.language = language
        self.type = self._determine_type()
    
    def _determine_type(self) -> str:
        """Determine the type of statement."""
        text = self.text.strip()
        
        if text.startswith("define predicate"):
            return "predicate_definition"
        elif text.startswith("define function"):
            return "function_definition"
        elif text.startswith("sbf"):
            return "stream_definition"
        elif text.startswith("rule"):
            return "stream_rule"
        elif text.startswith("for every"):
            return "universal_quantifier"
        elif text.startswith("there exists"):
            return "existential_quantifier"
        elif text.startswith("if"):
            return "implication"
        elif text.startswith("always"):
            return "temporal_always"
        elif text.startswith("sometimes"):
            return "temporal_sometimes"
        elif text.startswith("normalize"):
            return "normalize"
        else:
            return "expression"


class CoreSemanticAnalyzer:
    """Core semantic analyzer for TCE/TAU validation."""
    
    def __init__(self, vocabulary: Optional[Dict[str, Any]] = None):
        self.vocabulary = vocabulary or {}
        self.errors = []
    
    def analyze(self, ast: CoreAST) -> tuple[CoreAST, list]:
        """Analyze AST and return analyzed AST with errors."""
        # For now, just validate basic syntax
        if ast.language == 'TCE':
            if not ast.text.strip().endswith('.'):
                self.errors.append("Missing period at end of TCE input")
        
        # Return the AST and any errors
        return ast, self.errors


class TCEToTauTranslator:
    """Bidirectional translator between TCE and TAU."""
    
    def __init__(self):
        self.parser = CoreParser()
        self.analyzer = CoreSemanticAnalyzer()
    
    def translate_to_tau(self, ast: CoreAST) -> str:
        """Translate AST to TAU."""
        text = ast.text.strip()
        
        # Remove trailing period if present
        if text.endswith('.'):
            text = text[:-1]
        
        # Handle different statement types
        if ast.type == "predicate_definition":
            return self._translate_predicate_definition(text)
        elif ast.type == "function_definition":
            return self._translate_function_definition(text)
        elif ast.type == "stream_definition":
            return self._translate_stream_definition(text)
        elif ast.type == "stream_rule":
            return self._translate_stream_rule(text)
        elif ast.type == "universal_quantifier":
            return self._translate_universal_quantifier(text)
        elif ast.type == "existential_quantifier":
            return self._translate_existential_quantifier(text)
        elif ast.type == "implication":
            return self._translate_implication(text)
        elif ast.type == "temporal_always":
            return self._translate_temporal_always(text)
        elif ast.type == "temporal_sometimes":
            return self._translate_temporal_sometimes(text)
        elif ast.type == "normalize":
            return self._translate_normalize(text)
        else:
            return self._translate_expression(text)
    
    def translate_to_tce(self, ast: CoreAST) -> str:
        """Translate AST to TCE."""
        text = ast.text.strip()
        
        # Simple reverse translation
        if ":=" in text:
            # It's a definition
            parts = text.split(" := ")
            if len(parts) == 2:
                header, expr = parts
                if "(" in header:
                    # Function or predicate
                    tce_expr = self._translate_tau_to_tce_expr(expr)
                    return f"define predicate {header} as {tce_expr}."
        
        # Default: add period if missing
        if not text.endswith('.'):
            text += '.'
        
        return text
    
    def _translate_predicate_definition(self, text: str) -> str:
        """Translate predicate definition."""
        parts = text.split(" as ")
        if len(parts) != 2:
            raise SyntaxError("Invalid predicate definition")
        
        header = parts[0].replace("define predicate ", "")
        expr = self._translate_expression(parts[1])
        
        return f"{header} := {expr}"
    
    def _translate_function_definition(self, text: str) -> str:
        """Translate function definition."""
        parts = text.split(" as ")
        if len(parts) != 2:
            raise SyntaxError("Invalid function definition")
        
        header = parts[0].replace("define function ", "")
        expr = self._translate_expression(parts[1])
        
        return f"{header} := {expr}"
    
    def _translate_stream_definition(self, text: str) -> str:
        """Translate stream definition."""
        if "input file" in text:
            text = text.replace("input file", "i")
        elif "output file" in text:
            text = text.replace("output file", "o")
        return text
    
    def _translate_stream_rule(self, text: str) -> str:
        """Translate stream rule."""
        text = text[5:].strip()  # Remove "rule"
        
        parts = text.split(" = ", 1)
        if len(parts) != 2:
            raise SyntaxError("Invalid rule syntax")
        
        left = parts[0]
        right = self._translate_expression(parts[1])
        
        return f"{left} = {right}"
    
    def _translate_universal_quantifier(self, text: str) -> str:
        """Translate universal quantifier."""
        var_part = text[10:]  # Remove "for every "
        if " such that " in var_part:
            vars_text, expr_text = var_part.split(" such that ", 1)
            expr = self._translate_expression(expr_text)
            return f"{{all {vars_text}}} ({expr})"
        else:
            return f"{{all {var_part}}}"
    
    def _translate_existential_quantifier(self, text: str) -> str:
        """Translate existential quantifier."""
        var_part = text[13:]  # Remove "there exists "
        if " such that " in var_part:
            vars_text, expr_text = var_part.split(" such that ", 1)
            expr = self._translate_expression(expr_text)
            return f"{{ex {vars_text}}} ({expr})"
        else:
            return f"{{ex {var_part}}}"
    
    def _translate_implication(self, text: str) -> str:
        """Translate implication."""
        text = text[3:]  # Remove "if "
        
        parts = text.split(" then ", 1)
        if len(parts) != 2:
            raise SyntaxError("Invalid implication syntax")
        
        condition = self._translate_expression(parts[0])
        consequent = self._translate_expression(parts[1])
        
        return f"({condition}) -> {consequent}"
    
    def _translate_temporal_always(self, text: str) -> str:
        """Translate temporal always."""
        expr = text[7:].strip()  # Remove "always "
        
        # Check if expression is already wrapped in parentheses
        if expr.startswith('(') and expr.endswith(')'):
            # Remove outer parentheses as we'll add them back
            expr = expr[1:-1]
        
        translated_expr = self._translate_expression(expr)
        return f"always ({translated_expr})"
    
    def _translate_temporal_sometimes(self, text: str) -> str:
        """Translate temporal sometimes."""
        expr = text[10:].strip()  # Remove "sometimes "
        
        # Check if expression is already wrapped in parentheses
        if expr.startswith('(') and expr.endswith(')'):
            # Remove outer parentheses as we'll add them back
            expr = expr[1:-1]
        
        translated_expr = self._translate_expression(expr)
        return f"sometimes ({translated_expr})"
    
    def _translate_normalize(self, text: str) -> str:
        """Translate normalize statement."""
        expr = text[10:].strip()  # Remove "normalize "
        translated_expr = self._translate_expression(expr)
        return f"normalize {translated_expr}"
    
    def _translate_expression(self, expr: str) -> str:
        """Translate general expression."""
        # Handle stream output patterns
        if "output" in expr and "at time" in expr:
            # Pattern: "output N at time t = V"
            import re
            match = re.match(r"output (\d+) at time (\w+) = (.+)", expr)
            if match:
                stream_num = match.group(1)
                time_var = match.group(2)
                value = match.group(3)
                return f"o{stream_num}[{time_var}] = {value}"
        
        # Boolean operators
        expr = expr.replace(" xor ", " + ")
        expr = expr.replace(" and ", " & ")
        expr = expr.replace(" or ", " \\\\ ")
        
        # Handle "not" prefix
        if expr.startswith("not "):
            expr = expr[4:] + "'"
        
        # Handle complement
        expr = expr.replace(" complement", "'")
        
        # Comparisons
        expr = expr.replace(" equals ", " = ")
        expr = expr.replace(" is less than ", " < ")
        expr = expr.replace(" is greater than ", " > ")
        
        return expr
    
    def _translate_tau_to_tce_expr(self, expr: str) -> str:
        """Translate TAU expression back to TCE."""
        # Reverse boolean operators
        expr = expr.replace(" + ", " xor ")
        expr = expr.replace(" & ", " and ")
        expr = expr.replace(" \\\\ ", " or ")
        
        # Handle complement
        if expr.endswith("'"):
            expr = "not " + expr[:-1]
        
        return expr