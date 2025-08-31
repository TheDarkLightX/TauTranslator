"""
TCE (Tau Controlled English) suggestion engine following the Intentional Disclosure Principle.

Provides controlled English patterns that map to TAU language constructs,
helping users write formal specifications in natural language.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .models import (
    EducationalSuggestion,
    SuggestionCategory,
    DifficultyLevel,
    SpecificationContext,
    ContextType,
    SuggestionText,
    DisplayText,
    HintText,
    ExampleCode,
    TemplatePattern,
    TauCode,
    TcePattern,
    ConfidenceScore
)


@dataclass(frozen=True)
class TcePatternDefinition:
    """TCE pattern with TAU mapping."""
    english_pattern: str
    tau_equivalent: str
    description: str
    example: str
    category: SuggestionCategory
    difficulty: DifficultyLevel
    template: Optional[str] = None


class TceSuggestionEngine:
    """
    Intelligent TCE (Controlled English) suggestion engine.
    
    Bridges natural language and TAU formal specifications.
    Follows Rule 2: Public methods orchestrate, private methods implement.
    """
    
    def __init__(self):
        """Initialize with TCE pattern knowledge base."""
        self._patterns = self._initialize_tce_patterns()
        self._context_patterns = self._initialize_context_patterns()
    
    # =======================
    # Public Orchestrator Methods (Rule 2)
    # =======================
    
    def get_suggestions_for_context(
        self,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """
        Generate TCE suggestions based on specification context.
        
        Returns controlled English patterns with TAU equivalents.
        """
        # Rule 2: Clear orchestration workflow
        current_text = self._extract_current_phrase_from_context(context)
        pattern_suggestions = self._generate_pattern_suggestions(current_text, context)
        context_suggestions = self._generate_context_specific_suggestions(context)
        
        all_suggestions = pattern_suggestions + context_suggestions
        filtered_suggestions = self._filter_by_learning_level(all_suggestions, context.learning_level)
        ranked_suggestions = self._rank_suggestions_by_relevance(filtered_suggestions, context)
        
        return self._add_tau_mappings_to_suggestions(ranked_suggestions[:10])
    
    def get_tce_to_tau_mapping(
        self,
        tce_text: str
    ) -> Optional[TauCode]:
        """
        Get direct TAU translation for a TCE phrase.
        
        Used for real-time translation hints.
        """
        matching_pattern = self._find_matching_pattern(tce_text)
        if matching_pattern:
            return self._instantiate_tau_pattern(matching_pattern, tce_text)
        return None
    
    # =======================
    # Private Implementation Methods (Rule 2)
    # =======================
    
    def _initialize_tce_patterns(self) -> List[TcePatternDefinition]:
        """Initialize controlled English patterns."""
        return [
            # Quantification patterns
            TcePatternDefinition(
                english_pattern="for all $objects such that $condition",
                tau_equivalent="forall $objects : $condition",
                description="Universal quantification in controlled English",
                example="for all x such that x > 0",
                category=SuggestionCategory.QUANTIFIER,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="for all $ such that $"
            ),
            TcePatternDefinition(
                english_pattern="there exists $object such that $property",
                tau_equivalent="exists $object : $property",
                description="Existential quantification in controlled English",
                example="there exists x such that x * x = 4",
                category=SuggestionCategory.QUANTIFIER,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="there exists $ such that $"
            ),
            
            # Temporal patterns
            TcePatternDefinition(
                english_pattern="it is always the case that $property",
                tau_equivalent="always ($property)",
                description="Temporal invariant property",
                example="it is always the case that balance >= 0",
                category=SuggestionCategory.TEMPORAL,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="it is always the case that $"
            ),
            TcePatternDefinition(
                english_pattern="sometimes $property holds",
                tau_equivalent="sometimes ($property)",
                description="Temporal possibility",
                example="sometimes the system is idle",
                category=SuggestionCategory.TEMPORAL,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="sometimes $ holds"
            ),
            TcePatternDefinition(
                english_pattern="eventually $property will be true",
                tau_equivalent="eventually ($property)",
                description="Temporal eventuality",
                example="eventually the task will complete",
                category=SuggestionCategory.TEMPORAL,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="eventually $ will be true"
            ),
            
            # Conditional patterns
            TcePatternDefinition(
                english_pattern="if $condition then $consequence",
                tau_equivalent="$condition -> $consequence",
                description="Logical implication",
                example="if x > 0 then f(x) > 0",
                category=SuggestionCategory.OPERATOR,
                difficulty=DifficultyLevel.BEGINNER,
                template="if $ then $"
            ),
            TcePatternDefinition(
                english_pattern="$A if and only if $B",
                tau_equivalent="$A <-> $B",
                description="Logical equivalence",
                example="x is even if and only if x mod 2 equals 0",
                category=SuggestionCategory.OPERATOR,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="$ if and only if $"
            ),
            
            # Solver patterns
            TcePatternDefinition(
                english_pattern="find a value for $var such that $condition",
                tau_equivalent="solve $var = $condition",
                description="Find solution satisfying condition",
                example="find a value for x such that x squared equals 4",
                category=SuggestionCategory.SOLVER,
                difficulty=DifficultyLevel.BEGINNER,
                template="find a value for $ such that $"
            ),
            TcePatternDefinition(
                english_pattern="find values for $vars such that $conditions",
                tau_equivalent="solve $conditions",
                description="Find multiple values satisfying conditions",
                example="find values for x and y such that x + y = 10",
                category=SuggestionCategory.SOLVER,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="find values for $ such that $"
            ),
            
            # Stream patterns
            TcePatternDefinition(
                english_pattern="$output at time t equals $expression",
                tau_equivalent="$output[t] = $expression",
                description="Stream value at current time",
                example="output at time t equals input at time t",
                category=SuggestionCategory.STREAM,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="$ at time t equals $"
            ),
            TcePatternDefinition(
                english_pattern="$stream at the previous time",
                tau_equivalent="$stream[t-1]",
                description="Stream value at previous time step",
                example="state at the previous time",
                category=SuggestionCategory.STREAM,
                difficulty=DifficultyLevel.INTERMEDIATE,
                template="$ at the previous time"
            ),
            
            # Basic comparisons
            TcePatternDefinition(
                english_pattern="$A equals $B",
                tau_equivalent="$A = $B",
                description="Equality comparison",
                example="x equals 0",
                category=SuggestionCategory.OPERATOR,
                difficulty=DifficultyLevel.BEGINNER,
                template="$ equals $"
            ),
            TcePatternDefinition(
                english_pattern="$A is greater than $B",
                tau_equivalent="$A > $B",
                description="Greater than comparison",
                example="x is greater than 0",
                category=SuggestionCategory.OPERATOR,
                difficulty=DifficultyLevel.BEGINNER,
                template="$ is greater than $"
            ),
            TcePatternDefinition(
                english_pattern="$A is not equal to $B",
                tau_equivalent="$A != $B",
                description="Inequality comparison",
                example="status is not equal to error",
                category=SuggestionCategory.OPERATOR,
                difficulty=DifficultyLevel.BEGINNER,
                template="$ is not equal to $"
            )
        ]
    
    def _initialize_context_patterns(self) -> Dict[ContextType, List[str]]:
        """Initialize context-specific TCE patterns."""
        return {
            ContextType.QUANTIFIER_EXPRESSION: [
                "for all", "there exists", "for every", "for some"
            ],
            ContextType.TEMPORAL_CONSTRAINT: [
                "it is always", "sometimes", "eventually", "never"
            ],
            ContextType.SOLVER_COMMAND: [
                "find", "solve for", "determine", "calculate"
            ],
            ContextType.STREAM_RULE: [
                "at time", "at the previous", "at the next"
            ]
        }
    
    def _extract_current_phrase_from_context(self, context: SpecificationContext) -> str:
        """Extract current phrase being typed."""
        current_line = context.get_current_line()
        # Look for last few words to match patterns
        words = current_line.split()
        if len(words) >= 2:
            return " ".join(words[-2:])
        return words[-1] if words else ""
    
    def _generate_pattern_suggestions(
        self,
        current_text: str,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Generate TCE pattern suggestions matching current text."""
        suggestions = []
        current_lower = current_text.lower()
        
        for pattern in self._patterns:
            # Check if pattern starts with current text
            pattern_start = pattern.english_pattern.split()[0:2]
            pattern_prefix = " ".join(pattern_start).lower()
            
            if pattern_prefix.startswith(current_lower) or current_lower in pattern_prefix:
                suggestion = self._create_suggestion_from_pattern(pattern)
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_context_specific_suggestions(
        self,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Generate suggestions based on context type."""
        if context.context_type not in self._context_patterns:
            return []
        
        suggestions = []
        context_keywords = self._context_patterns[context.context_type]
        
        for keyword in context_keywords:
            # Find matching patterns
            for pattern in self._patterns:
                if keyword in pattern.english_pattern.lower():
                    suggestion = self._create_suggestion_from_pattern(pattern)
                    suggestions.append(suggestion)
                    break
        
        return suggestions
    
    def _create_suggestion_from_pattern(
        self,
        pattern: TcePatternDefinition
    ) -> EducationalSuggestion:
        """Create educational suggestion from TCE pattern."""
        return EducationalSuggestion(
            text=SuggestionText(pattern.english_pattern),
            display=DisplayText(pattern.english_pattern.replace("$", "...")),
            category=pattern.category,
            description=HintText(pattern.description),
            example=ExampleCode(pattern.example),
            difficulty=pattern.difficulty,
            template=TemplatePattern(pattern.template) if pattern.template else None,
            tau_equivalent=TauCode(pattern.tau_equivalent),
            confidence=ConfidenceScore(0.9)
        )
    
    def _filter_by_learning_level(
        self,
        suggestions: List[EducationalSuggestion],
        level: DifficultyLevel
    ) -> List[EducationalSuggestion]:
        """Filter suggestions by learning level."""
        if level == DifficultyLevel.BEGINNER:
            return [s for s in suggestions if s.difficulty == DifficultyLevel.BEGINNER]
        elif level == DifficultyLevel.INTERMEDIATE:
            return [s for s in suggestions if s.difficulty in [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE
            ]]
        else:  # ADVANCED
            return suggestions
    
    def _rank_suggestions_by_relevance(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Rank suggestions by relevance to current context."""
        # Simple ranking by confidence and text match
        current_text = context.get_current_line().lower()
        
        def relevance_score(suggestion: EducationalSuggestion) -> float:
            text_match = 1.0 if current_text in suggestion.text.lower() else 0.5
            return suggestion.confidence * text_match
        
        return sorted(suggestions, key=relevance_score, reverse=True)
    
    def _add_tau_mappings_to_suggestions(
        self,
        suggestions: List[EducationalSuggestion]
    ) -> List[EducationalSuggestion]:
        """Ensure all suggestions have TAU mappings."""
        # All our TCE suggestions already have TAU equivalents
        return suggestions
    
    def _find_matching_pattern(self, tce_text: str) -> Optional[TcePatternDefinition]:
        """Find TCE pattern matching given text."""
        tce_lower = tce_text.lower()
        
        for pattern in self._patterns:
            if self._pattern_matches_text(pattern.english_pattern, tce_lower):
                return pattern
        
        return None
    
    def _pattern_matches_text(self, pattern: str, text: str) -> bool:
        """Check if pattern matches text (with wildcards)."""
        # Simple matching - could be enhanced with regex
        pattern_parts = pattern.lower().split("$")
        
        if len(pattern_parts) == 1:
            return pattern_parts[0].strip() in text
        
        # Check if all non-variable parts are in text in order
        current_pos = 0
        for part in pattern_parts:
            if part:  # Skip empty parts
                part = part.strip()
                pos = text.find(part, current_pos)
                if pos == -1:
                    return False
                current_pos = pos + len(part)
        
        return True
    
    def _instantiate_tau_pattern(
        self,
        pattern: TcePatternDefinition,
        tce_text: str
    ) -> TauCode:
        """Instantiate TAU pattern with actual values from TCE text."""
        # This would need more sophisticated parsing in production
        # For now, return the pattern template
        return TauCode(pattern.tau_equivalent)