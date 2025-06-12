"""
Core parsing service with business logic.

Copyright: DarkLightX / Dana Edwards
"""

import logging
from typing import Any, Optional
from .domain_types import (
    SourceCode, ParserError, ParseResult, ASTTransformer
)

try:
    from lark import LarkError, Tree
    LARK_AVAILABLE = True
except ImportError:
    LarkError = Exception
    Tree = object
    LARK_AVAILABLE = False


class ParseResultValidator:
    """Validates parsing results."""
    
    @staticmethod
    def validate_parse_result(result: Any, source_code: SourceCode) -> ParseResult:
        """Validate that parse result is valid."""
        if result is None:
            raise ParserError(f"Parsing failed for source: {source_code}")
        
        return result


class ErrorContextBuilder:
    """Builds detailed error context for parsing failures."""
    
    @staticmethod
    def build_error_context(error: Exception, source_code: SourceCode) -> str:
        """Build detailed error context from parsing exception."""
        error_message = f"Parsing failed for source: '{source_code}'\nError: {error}"
        
        if hasattr(error, 'context') and error.context:
            error_message += f"\nContext: {error.context}"
        
        if hasattr(error, 'allowed') and error.allowed:
            error_message += f"\nAllowed tokens: {error.allowed}"
        
        if hasattr(error, 'considered_tokens') and error.considered_tokens:
            error_message += f"\nConsidered tokens: {error.considered_tokens}"
        
        return error_message


class TransformationService:
    """Handles CST to AST transformation."""
    
    def __init__(self, transformer: Optional[ASTTransformer]):
        """Initialize with optional transformer."""
        self._transformer = transformer
        self._logger = logging.getLogger(__name__)
    
    def transform_to_ast(self, cst: ParseResult, source_code: SourceCode) -> Any:
        """Transform CST to AST if transformer available."""
        if not self._transformer:
            self._logger.debug("No transformer available, returning CST")
            return cst
        
        self._logger.debug(f"Transforming CST to AST using: {type(self._transformer)}")
        
        if self._is_diagnostic_case(source_code):
            self._log_diagnostic_info(cst)
        
        try:
            ast = self._transformer.transform(cst)
            self._logger.debug(f"Successfully transformed CST to AST. Root type: {type(ast)}")
            return ast
        except Exception as e:
            error_msg = f"AST transformation failed: {e}"
            self._logger.error(error_msg, exc_info=True)
            raise ParserError(error_msg) from e
    
    def _is_diagnostic_case(self, source_code: SourceCode) -> bool:
        """Check if this is a diagnostic case for debugging."""
        return source_code == "-5"  # Known failing case
    
    def _log_diagnostic_info(self, cst: ParseResult) -> None:
        """Log diagnostic information for debugging."""
        self._logger.error(f"DIAGNOSTIC: Transformer type: {type(self._transformer)}")
        self._logger.error(f"DIAGNOSTIC: Transformer methods: {dir(self._transformer)}")
        self._logger.error(f"DIAGNOSTIC: CST:\n{cst.pretty() if hasattr(cst, 'pretty') else str(cst)}")


class ParsingService:
    """Core parsing service that orchestrates the parsing process."""
    
    def __init__(self, parser_instance: Any, transformer: Optional[ASTTransformer]):
        """Initialize parsing service with parser and transformer."""
        self._parser = parser_instance
        self._transformation_service = TransformationService(transformer)
        self._logger = logging.getLogger(__name__)
    
    def parse_source(self, source_code: SourceCode) -> Any:
        """Parse source code and return AST or CST."""
        self._validate_parser_ready()
        
        self._logger.debug(f"Parsing source code: '{source_code}'")
        
        try:
            cst = self._parse_to_cst(source_code)
            return self._transformation_service.transform_to_ast(cst, source_code)
        except LarkError as e:
            error_context = ErrorContextBuilder.build_error_context(e, source_code)
            self._logger.error(error_context)
            raise ParserError(error_context) from e
        except Exception as e:
            error_msg = f"Unexpected parsing error: {e}"
            self._logger.error(error_msg, exc_info=True)
            raise ParserError(error_msg) from e
    
    def transform_cst(self, cst: Tree, source_code: SourceCode = SourceCode("")) -> Any:
        """Transform existing CST to AST."""
        return self._transformation_service.transform_to_ast(cst, source_code)
    
    def _validate_parser_ready(self) -> None:
        """Validate that parser is ready for use."""
        if not self._parser:
            raise ParserError("Parser not initialized")
    
    def _parse_to_cst(self, source_code: SourceCode) -> ParseResult:
        """Parse source code to CST."""
        cst = self._parser.parse(source_code)
        
        self._logger.debug(f"Successfully parsed to CST:\n{cst.pretty() if hasattr(cst, 'pretty') else str(cst)}")
        
        return ParseResultValidator.validate_parse_result(cst, source_code)