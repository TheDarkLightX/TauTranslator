"""
Error recovery mechanisms for parser following the Intentional Disclosure Principle.

Implements various strategies for recovering from parse errors to provide
better error messages and continue parsing when possible.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Set, Tuple, Dict
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing

from .types import (
    ParserContext, Token, ParseError, ErrorMessage, RecoveryAction,
    RecoveryResult, SourceLocation, TokenValue
)


class ErrorRecoveryStrategy:
    """
    Base class for error recovery strategies.
    Each strategy attempts to recover from specific error patterns.
    """
    
    def attempt_recovery(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Attempt to recover from parse error."""
        # Try different recovery techniques in order
        strategies = [
            self._try_synchronize_at_delimiter,
            self._try_skip_invalid_token,
            self._try_insert_missing_token,
            self._try_skip_to_keyword,
            self._try_panic_mode_recovery
        ]
        
        for strategy in strategies:
            result = strategy(error, context)
            if isinstance(result, Success):
                return result
        
        return Failure("Unable to recover from parse error")
    
    def _try_synchronize_at_delimiter(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Synchronize at statement delimiter (e.g., semicolon)."""
        sync_tokens = self._get_synchronization_tokens()
        
        new_context, skipped = self._skip_until_token_types(
            context,
            sync_tokens
        )
        
        if new_context.position > context.position:
            return Success(RecoveryResult(
                action=RecoveryAction.SYNCHRONIZE,
                new_context=new_context,
                skipped_tokens=skipped
            ))
        
        return Failure("No synchronization point found")
    
    def _try_skip_invalid_token(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Skip single invalid token."""
        if context.at_end():
            return Failure("Cannot skip - at end of input")
        
        current = context.current_token()
        if current and self._is_likely_typo(current):
            return Success(RecoveryResult(
                action=RecoveryAction.SKIP_TOKEN,
                new_context=context.advance(),
                skipped_tokens=[current]
            ))
        
        return Failure("Token not suitable for skipping")
    
    def _try_insert_missing_token(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Insert missing token if obvious."""
        if not error.expected_tokens:
            return Failure("No expected tokens to insert")
        
        # Check if we can insert a simple token
        for expected in error.expected_tokens:
            if self._can_auto_insert(expected, context):
                inserted = self._create_synthetic_token(expected, context)
                return Success(RecoveryResult(
                    action=RecoveryAction.INSERT_TOKEN,
                    new_context=context,  # Don't advance
                    inserted_token=inserted
                ))
        
        return Failure("Cannot determine token to insert")
    
    def _try_skip_to_keyword(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Skip to next major keyword."""
        keywords = self._get_major_keywords()
        
        new_context, skipped = self._skip_until_token_types(
            context,
            keywords
        )
        
        if len(skipped) > 0 and len(skipped) < 10:  # Reasonable skip
            return Success(RecoveryResult(
                action=RecoveryAction.SKIP_TO_DELIMITER,
                new_context=new_context,
                skipped_tokens=skipped
            ))
        
        return Failure("No suitable keyword found nearby")
    
    def _try_panic_mode_recovery(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Panic mode - skip to next statement boundary."""
        # Use recovery points if available
        if context.error_recovery_points:
            latest_point = context.error_recovery_points[-1]
            if latest_point < context.position:
                # Skip forward from recovery point
                recovery_context = ParserContext(
                    tokens=context.tokens,
                    position=latest_point,
                    error_recovery_points=context.error_recovery_points[:-1]
                )
                
                return Success(RecoveryResult(
                    action=RecoveryAction.RESTART_AT_STATEMENT,
                    new_context=recovery_context
                ))
        
        return Failure("No recovery points available")
    
    def _skip_until_token_types(
        self,
        context: ParserContext,
        token_types: Set[str]
    ) -> Tuple[ParserContext, List[Token]]:
        """Skip tokens until one of specified types found."""
        skipped = []
        current_ctx = context
        
        while not current_ctx.at_end():
            token = current_ctx.current_token()
            if token and token.type in token_types:
                break
            
            if token:
                skipped.append(token)
            current_ctx = current_ctx.advance()
        
        return current_ctx, skipped
    
    def _get_synchronization_tokens(self) -> Set[str]:
        """Get token types suitable for synchronization."""
        return {"SEMICOLON", "RBRACE", "NEWLINE", "EOF"}
    
    def _get_major_keywords(self) -> Set[str]:
        """Get major keywords for recovery."""
        return {
            "IF", "WHILE", "FOR", "FUNCTION", "CLASS",
            "RETURN", "BREAK", "CONTINUE", "VAR", "LET", "CONST"
        }
    
    def _is_likely_typo(self, token: Token) -> bool:
        """Check if token is likely a typo."""
        # Check for common typo patterns
        typo_patterns = [
            lambda t: t.type == "IDENTIFIER" and len(t.value) == 1,
            lambda t: t.type == "UNKNOWN",
            lambda t: t.type == "ERROR"
        ]
        
        return any(pattern(token) for pattern in typo_patterns)
    
    def _can_auto_insert(self, token_type: str, context: ParserContext) -> bool:
        """Check if token type can be auto-inserted."""
        auto_insertable = {
            "SEMICOLON": lambda ctx: True,  # Always can insert semicolon
            "RPAREN": lambda ctx: self._has_unmatched_lparen(ctx),
            "RBRACE": lambda ctx: self._has_unmatched_lbrace(ctx),
            "RBRACKET": lambda ctx: self._has_unmatched_lbracket(ctx),
        }
        
        checker = auto_insertable.get(token_type)
        return checker(context) if checker else False
    
    def _create_synthetic_token(
        self,
        token_type: str,
        context: ParserContext
    ) -> Token:
        """Create synthetic token for insertion."""
        # Get position from previous token or use current
        if context.position > 0:
            prev_token = context.tokens[context.position - 1]
            line = prev_token.end_line or prev_token.line
            column = (prev_token.end_column or prev_token.column) + 1
        else:
            line = 1
            column = 1
        
        # Determine synthetic value
        synthetic_values = {
            "SEMICOLON": ";",
            "RPAREN": ")",
            "RBRACE": "}",
            "RBRACKET": "]",
        }
        
        value = synthetic_values.get(token_type, "")
        
        return Token(
            type=token_type,
            value=TokenValue(value),
            line=line,
            column=column
        )
    
    def _has_unmatched_lparen(self, context: ParserContext) -> bool:
        """Check for unmatched left parenthesis."""
        return self._count_unmatched_tokens(context, "LPAREN", "RPAREN") > 0
    
    def _has_unmatched_lbrace(self, context: ParserContext) -> bool:
        """Check for unmatched left brace."""
        return self._count_unmatched_tokens(context, "LBRACE", "RBRACE") > 0
    
    def _has_unmatched_lbracket(self, context: ParserContext) -> bool:
        """Check for unmatched left bracket."""
        return self._count_unmatched_tokens(context, "LBRACKET", "RBRACKET") > 0
    
    def _count_unmatched_tokens(
        self,
        context: ParserContext,
        open_type: str,
        close_type: str
    ) -> int:
        """Count unmatched opening tokens."""
        count = 0
        for i in range(context.position):
            token = context.tokens[i]
            if token.type == open_type:
                count += 1
            elif token.type == close_type:
                count -= 1
        
        return max(0, count)


class TauSpecificRecovery(ErrorRecoveryStrategy):
    """
    Recovery strategy specific to Tau language constructs.
    Handles Tau-specific error patterns.
    """
    
    def _get_synchronization_tokens(self) -> Set[str]:
        """Tau-specific synchronization points."""
        base = super()._get_synchronization_tokens()
        tau_specific = {
            "DOT",  # End of statement in Tau
            "FOR", "EXISTS", "IF", "THEN",  # Tau keywords
            "IMPLIES", "AND", "OR"  # Logical operators
        }
        return base.union(tau_specific)
    
    def _get_major_keywords(self) -> Set[str]:
        """Tau-specific major keywords."""
        return {
            "FOR", "ALL", "EXISTS", "IF", "THEN", "ELSE",
            "PREDICATE", "FUNCTION", "RETURNS", "IS",
            "TRUE", "FALSE", "NOT", "AND", "OR", "IMPLIES"
        }
    
    def _try_recover_quantifier(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Result[RecoveryResult, str]:
        """Try to recover from quantifier parsing errors."""
        current = context.current_token()
        if not current:
            return Failure("No token to examine")
        
        # Common Tau quantifier errors
        if current.value.lower() in ["forall", "for_all"]:
            # User typed "forall" instead of "for all"
            return self._split_compound_token(context, "for", "all")
        
        if current.value.lower() == "exist":
            # Missing 's' in exists
            corrected = Token(
                type="EXISTS",
                value=TokenValue("exists"),
                line=current.line,
                column=current.column
            )
            return Success(RecoveryResult(
                action=RecoveryAction.INSERT_TOKEN,
                new_context=context.advance(),
                inserted_token=corrected
            ))
        
        return Failure("Not a quantifier error")
    
    def _split_compound_token(
        self,
        context: ParserContext,
        first: str,
        second: str
    ) -> Result[RecoveryResult, str]:
        """Split compound token into two tokens."""
        current = context.current_token()
        if not current:
            return Failure("No token to split")
        
        # Create two synthetic tokens
        token1 = Token(
            type=first.upper(),
            value=TokenValue(first),
            line=current.line,
            column=current.column
        )
        
        token2 = Token(
            type=second.upper(),
            value=TokenValue(second),
            line=current.line,
            column=current.column + len(first) + 1
        )
        
        # Insert both tokens
        new_tokens = (
            context.tokens[:context.position] +
            [token1, token2] +
            context.tokens[context.position + 1:]
        )
        
        new_context = ParserContext(
            tokens=new_tokens,
            position=context.position,
            error_recovery_points=context.error_recovery_points
        )
        
        return Success(RecoveryResult(
            action=RecoveryAction.INSERT_TOKEN,
            new_context=new_context,
            inserted_token=token1
        ))


class ErrorMessageBuilder:
    """Builds helpful error messages with recovery hints."""
    
    def build_error_message(
        self,
        error: ParseError,
        context: ParserContext,
        recovery: Optional[RecoveryResult] = None
    ) -> str:
        """Build comprehensive error message."""
        parts = []
        
        # Main error
        parts.append(self._format_main_error(error))
        
        # Context
        parts.append(self._format_error_context(error, context))
        
        # Expected vs found
        if error.expected_tokens and error.found_token:
            parts.append(self._format_expected_found(error))
        
        # Recovery hint
        if recovery:
            parts.append(self._format_recovery_hint(recovery))
        elif error.recovery_hint:
            parts.append(f"Hint: {error.recovery_hint}")
        
        # Similar valid constructs
        similar = self._suggest_similar_constructs(error, context)
        if similar:
            parts.append(f"Did you mean: {similar}")
        
        return "\n".join(parts)
    
    def _format_main_error(self, error: ParseError) -> str:
        """Format main error message."""
        if error.location:
            return f"Parse error at {error.location.to_string()}: {error.message}"
        return f"Parse error: {error.message}"
    
    def _format_error_context(
        self,
        error: ParseError,
        context: ParserContext
    ) -> str:
        """Format error context with line excerpt."""
        if not error.location:
            return ""
        
        # Get surrounding tokens for context
        start = max(0, context.position - 3)
        end = min(len(context.tokens), context.position + 2)
        
        context_tokens = context.tokens[start:end]
        context_str = " ".join(str(t.value) for t in context_tokens)
        
        # Mark error position
        if start < context.position < end:
            marker_pos = sum(
                len(str(context.tokens[i].value)) + 1
                for i in range(start, context.position)
            )
            marker = " " * marker_pos + "^"
            return f"\n  {context_str}\n  {marker}"
        
        return f"\n  Context: {context_str}"
    
    def _format_expected_found(self, error: ParseError) -> str:
        """Format expected vs found tokens."""
        expected = ", ".join(error.expected_tokens[:5])
        if len(error.expected_tokens) > 5:
            expected += ", ..."
        
        found = f"{error.found_token.type}"
        if error.found_token.value:
            found += f" '{error.found_token.value}'"
        
        return f"\n  Expected: {expected}\n  Found: {found}"
    
    def _format_recovery_hint(self, recovery: RecoveryResult) -> str:
        """Format recovery action as hint."""
        hints = {
            RecoveryAction.SYNCHRONIZE: "Recovered by synchronizing at delimiter",
            RecoveryAction.SKIP_TOKEN: f"Skipped invalid token",
            RecoveryAction.INSERT_TOKEN: f"Inserted missing {recovery.inserted_token.type if recovery.inserted_token else 'token'}",
            RecoveryAction.SKIP_TO_DELIMITER: f"Skipped {len(recovery.skipped_tokens)} tokens to recover",
            RecoveryAction.RESTART_AT_STATEMENT: "Restarted parsing at statement boundary"
        }
        
        return f"\n  Recovery: {hints.get(recovery.action, 'Recovered from error')}"
    
    def _suggest_similar_constructs(
        self,
        error: ParseError,
        context: ParserContext
    ) -> Optional[str]:
        """Suggest similar valid constructs."""
        if not error.found_token:
            return None
        
        # Map common mistakes to suggestions
        suggestions = {
            "forall": "for all",
            "exist": "exists",
            "IF": "if",  # Case sensitivity
            "THEN": "then",
            "=": "= (assignment) or == (comparison)",
            "=>": "implies or ->",
        }
        
        found_value = str(error.found_token.value)
        return suggestions.get(found_value)


class IncrementalRecovery:
    """
    Supports incremental parsing with error recovery.
    Maintains parse state for efficient re-parsing.
    """
    
    def __init__(self):
        """Initialize incremental recovery."""
        self._checkpoints: List[ParserContext] = []
        self._error_regions: List[Tuple[int, int]] = []
    
    def add_checkpoint(self, context: ParserContext) -> None:
        """Add parsing checkpoint for recovery."""
        self._checkpoints.append(context)
    
    def mark_error_region(self, start: int, end: int) -> None:
        """Mark region containing errors."""
        self._error_regions.append((start, end))
    
    def find_recovery_checkpoint(
        self,
        error_position: int
    ) -> Optional[ParserContext]:
        """Find best checkpoint for recovery."""
        # Find latest checkpoint before error
        best_checkpoint = None
        
        for checkpoint in reversed(self._checkpoints):
            if checkpoint.position < error_position:
                best_checkpoint = checkpoint
                break
        
        return best_checkpoint
    
    def can_reuse_parse(
        self,
        start: int,
        end: int
    ) -> bool:
        """Check if parse results can be reused for range."""
        # Check if range overlaps with any error region
        for error_start, error_end in self._error_regions:
            if start < error_end and end > error_start:
                return False
        
        return True
    
    def clear_checkpoints_after(self, position: int) -> None:
        """Clear checkpoints after given position."""
        self._checkpoints = [
            cp for cp in self._checkpoints
            if cp.position <= position
        ]
    
    def clear_error_regions(self) -> None:
        """Clear all error regions."""
        self._error_regions.clear()