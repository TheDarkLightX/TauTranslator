"""
TAU language suggestion engine following the Intentional Disclosure Principle.

Provides intelligent, educational suggestions for TAU language constructs.
All methods follow naming conventions that reveal their purpose and effects.

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
    ConfidenceScore
)


@dataclass(frozen=True)
class TauKeyword:
    """TAU language keyword with educational metadata."""
    keyword: str
    category: SuggestionCategory
    description: str
    example: str
    template: Optional[str]
    difficulty: DifficultyLevel


class TauSuggestionEngine:
    """
    Intelligent TAU language suggestion engine with educational focus.
    
    Follows Rule 2: Public methods orchestrate, private methods implement.
    """
    
    def __init__(self):
        """Initialize with TAU language knowledge base."""
        self._keywords = self._initialize_tau_keywords()
        self._patterns = self._initialize_tau_patterns()
        self._templates = self._initialize_tau_templates()
    
    # =======================
    # Public Orchestrator Methods (Rule 2)
    # =======================
    
    def get_suggestions_for_context(
        self, 
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """
        Generate educational suggestions based on specification context.
        
        High-level orchestration of suggestion generation process.
        """
        # Rule 2: Orchestrator method with clear workflow
        current_text = self._extract_current_token_from_context(context)
        keyword_suggestions = self._generate_keyword_suggestions(current_text, context)
        pattern_suggestions = self._generate_pattern_suggestions(context)
        template_suggestions = self._generate_template_suggestions(context)
        
        all_suggestions = keyword_suggestions + pattern_suggestions + template_suggestions
        filtered_suggestions = self._filter_by_learning_level(all_suggestions, context.learning_level)
        ranked_suggestions = self._rank_suggestions_by_relevance(filtered_suggestions, context)
        
        return ranked_suggestions[:10]  # Return top 10
    
    def get_context_specific_templates(
        self,
        context_type: ContextType,
        difficulty: DifficultyLevel
    ) -> List[EducationalSuggestion]:
        """
        Get templates specific to a context type and difficulty level.
        
        Provides scaffolding for common TAU constructs.
        """
        relevant_templates = self._select_templates_for_context(context_type)
        filtered_templates = self._filter_templates_by_difficulty(relevant_templates, difficulty)
        return self._convert_templates_to_suggestions(filtered_templates)
    
    # =======================
    # Private Implementation Methods (Rule 2)
    # =======================
    
    def _initialize_tau_keywords(self) -> List[TauKeyword]:
        """Initialize TAU language keywords with educational metadata."""
        return [
            # Temporal operators
            TauKeyword(
                keyword="always",
                category=SuggestionCategory.TEMPORAL,
                description="Temporal operator: specifies an invariant property that holds at all times",
                example="always (x > 0)",
                template="always ($property)",
                difficulty=DifficultyLevel.INTERMEDIATE
            ),
            TauKeyword(
                keyword="sometimes",
                category=SuggestionCategory.TEMPORAL,
                description="Temporal operator: specifies that a property holds at some point",
                example="sometimes (goal_reached)",
                template="sometimes ($property)",
                difficulty=DifficultyLevel.INTERMEDIATE
            ),
            TauKeyword(
                keyword="eventually",
                category=SuggestionCategory.TEMPORAL,
                description="Temporal operator: specifies that a property will hold in the future",
                example="eventually (task_completed)",
                template="eventually ($property)",
                difficulty=DifficultyLevel.INTERMEDIATE
            ),
            
            # Quantifiers
            TauKeyword(
                keyword="forall",
                category=SuggestionCategory.QUANTIFIER,
                description="Universal quantification: states a property holds for all values",
                example="forall x : x > 0 -> f(x) > 0",
                template="forall $var : $condition",
                difficulty=DifficultyLevel.INTERMEDIATE
            ),
            TauKeyword(
                keyword="exists",
                category=SuggestionCategory.QUANTIFIER,
                description="Existential quantification: states there exists at least one value",
                example="exists x : x * x = 4",
                template="exists $var : $property",
                difficulty=DifficultyLevel.INTERMEDIATE
            ),
            
            # Keywords
            TauKeyword(
                keyword="DEFINE",
                category=SuggestionCategory.DEFINITION,
                description="Define a new function or predicate",
                example="DEFINE add(x, y) := x + y",
                template="DEFINE $name($args) := $body",
                difficulty=DifficultyLevel.BEGINNER
            ),
            TauKeyword(
                keyword="solve",
                category=SuggestionCategory.SOLVER,
                description="Find values that satisfy constraints",
                example="solve x = 0",
                template="solve $constraint",
                difficulty=DifficultyLevel.BEGINNER
            ),
            
            # Boolean constants
            TauKeyword(
                keyword="true",
                category=SuggestionCategory.KEYWORD,
                description="Boolean constant: true value",
                example="result = true",
                template=None,
                difficulty=DifficultyLevel.BEGINNER
            ),
            TauKeyword(
                keyword="false",
                category=SuggestionCategory.KEYWORD,
                description="Boolean constant: false value",
                example="initialized = false",
                template=None,
                difficulty=DifficultyLevel.BEGINNER
            ),
            
            # Advanced constructs
            TauKeyword(
                keyword="never",
                category=SuggestionCategory.TEMPORAL,
                description="Temporal operator: specifies that a property never holds",
                example="never (error_state)",
                template="never ($property)",
                difficulty=DifficultyLevel.ADVANCED
            ),
            TauKeyword(
                keyword="CONCEPT",
                category=SuggestionCategory.DEFINITION,
                description="Define a new concept or type",
                example="CONCEPT Person { name: string, age: int }",
                template="CONCEPT $name { $fields }",
                difficulty=DifficultyLevel.ADVANCED
            )
        ]
    
    def _initialize_tau_patterns(self) -> Dict[ContextType, List[str]]:
        """Initialize context-specific patterns."""
        return {
            ContextType.SOLVER_COMMAND: [
                "$var = $expr",
                "$eq1 && $eq2",
                "{$var}:$type $constraint",
                "{ex $var $constraint} $equation"
            ],
            ContextType.STREAM_RULE: [
                "$output[t] = $input[t]",
                "$stream[t-1]",
                "$stream[t+1]"
            ],
            ContextType.TEMPORAL_CONSTRAINT: [
                "always ($property)",
                "sometimes ($property)",
                "eventually ($property)",
                "$property[t] -> $property[t+1]"
            ]
        }
    
    def _initialize_tau_templates(self) -> Dict[str, EducationalSuggestion]:
        """Initialize TAU template suggestions."""
        # Implementation continues...
        return {}
    
    def _extract_current_token_from_context(self, context: SpecificationContext) -> str:
        """Extract the current token being typed."""
        current_line = context.get_current_line()
        words = current_line.split()
        return words[-1] if words else ""
    
    def _generate_keyword_suggestions(
        self,
        current_text: str,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Generate keyword suggestions matching current text."""
        suggestions = []
        
        for keyword in self._keywords:
            if keyword.keyword.lower().startswith(current_text.lower()):
                suggestion = EducationalSuggestion(
                    text=SuggestionText(keyword.keyword),
                    display=DisplayText(keyword.keyword),
                    category=keyword.category,
                    description=HintText(keyword.description),
                    example=ExampleCode(keyword.example),
                    difficulty=keyword.difficulty,
                    template=TemplatePattern(keyword.template) if keyword.template else None,
                    confidence=ConfidenceScore(0.9)
                )
                suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_pattern_suggestions(
        self,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Generate context-specific pattern suggestions."""
        # Special handling for temporal indices
        if "[" in context.get_current_line():
            return self._generate_temporal_index_suggestions()
        
        # For solver commands, always suggest patterns
        if context.context_type == ContextType.SOLVER_COMMAND:
            # Check if we're right after "solve "
            if context.get_current_line().strip() == "solve":
                return self._generate_solver_patterns(context.learning_level)
        
        # Other context-specific patterns
        if context.context_type not in self._patterns:
            return []
        
        suggestions = []
        patterns = self._patterns[context.context_type]
        
        # Convert patterns to suggestions
        for pattern in patterns:
            suggestion = self._create_pattern_suggestion(pattern, context)
            suggestions.append(suggestion)
        
        return suggestions
    
    def _generate_solver_patterns(self, level: DifficultyLevel) -> List[EducationalSuggestion]:
        """Generate solver-specific pattern suggestions."""
        patterns = []
        
        # Basic equation pattern for all levels
        patterns.append(
            EducationalSuggestion(
                text=SuggestionText("x = 0"),
                display=DisplayText("x = 0"),
                category=SuggestionCategory.PATTERN,
                description=HintText("Simple equation"),
                example=ExampleCode("solve x = 0"),
                difficulty=DifficultyLevel.BEGINNER,
                template=TemplatePattern("$var = $expr"),
                confidence=ConfidenceScore(0.9)
            )
        )
        
        if level != DifficultyLevel.BEGINNER:
            # Add more complex patterns for intermediate/advanced
            patterns.append(
                EducationalSuggestion(
                    text=SuggestionText("x = 0 && y = 0"),
                    display=DisplayText("x = 0 && y = 0"),
                    category=SuggestionCategory.PATTERN,
                    description=HintText("System of equations"),
                    example=ExampleCode("solve x = 0 && y = 0"),
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    template=TemplatePattern("$eq1 && $eq2"),
                    confidence=ConfidenceScore(0.8)
                )
            )
        
        return patterns
    
    def _generate_temporal_index_suggestions(self) -> List[EducationalSuggestion]:
        """Generate suggestions for temporal indices."""
        return [
            EducationalSuggestion(
                text=SuggestionText("t"),
                display=DisplayText("t"),
                category=SuggestionCategory.TEMPORAL,
                description=HintText("Current time"),
                example=ExampleCode("x[t] = y[t]"),
                difficulty=DifficultyLevel.BEGINNER,
                confidence=ConfidenceScore(1.0)
            ),
            EducationalSuggestion(
                text=SuggestionText("t-1"),
                display=DisplayText("t-1"),
                category=SuggestionCategory.TEMPORAL,
                description=HintText("Previous time step"),
                example=ExampleCode("state[t] = state[t-1] && input[t]"),
                difficulty=DifficultyLevel.INTERMEDIATE,
                confidence=ConfidenceScore(0.9)
            ),
            EducationalSuggestion(
                text=SuggestionText("t+1"),
                display=DisplayText("t+1"),
                category=SuggestionCategory.TEMPORAL,
                description=HintText("Next time step"),
                example=ExampleCode("output[t+1] = process(input[t])"),
                difficulty=DifficultyLevel.INTERMEDIATE,
                confidence=ConfidenceScore(0.8)
            )
        ]
    
    def _generate_template_suggestions(
        self,
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Generate template suggestions based on context."""
        # Implementation for template generation
        return []
    
    def _filter_by_learning_level(
        self,
        suggestions: List[EducationalSuggestion],
        level: DifficultyLevel
    ) -> List[EducationalSuggestion]:
        """Filter suggestions by learning level."""
        if level == DifficultyLevel.BEGINNER:
            # For beginners, include temporal keywords but not quantifiers
            filtered = []
            for s in suggestions:
                if s.difficulty == DifficultyLevel.BEGINNER:
                    filtered.append(s)
                elif s.category == SuggestionCategory.TEMPORAL and s.text == "always":
                    # Include "always" for beginners as it's fundamental
                    filtered.append(s)
            return filtered
        elif level == DifficultyLevel.INTERMEDIATE:
            return [s for s in suggestions if s.difficulty in [
                DifficultyLevel.BEGINNER,
                DifficultyLevel.INTERMEDIATE
            ]]
        else:  # ADVANCED
            return suggestions  # Show all
    
    def _rank_suggestions_by_relevance(
        self,
        suggestions: List[EducationalSuggestion],
        context: SpecificationContext
    ) -> List[EducationalSuggestion]:
        """Rank suggestions by relevance to current context."""
        # Simple ranking by confidence score
        return sorted(suggestions, key=lambda s: s.confidence, reverse=True)
    
    def _create_pattern_suggestion(
        self,
        pattern: str,
        context: SpecificationContext
    ) -> EducationalSuggestion:
        """Create suggestion from pattern template."""
        # Map patterns to descriptions
        description_map = {
            "$var = $expr": "Simple equation",
            "$eq1 && $eq2": "System of equations",
            "{$var}:$type $constraint": "Type annotation for solver",
            "$output[t] = $input[t]": "Stream processing rule"
        }
        
        return EducationalSuggestion(
            text=SuggestionText(pattern),
            display=DisplayText(pattern.replace("$", "")),
            category=SuggestionCategory.PATTERN,
            description=HintText(description_map.get(pattern, "Pattern template")),
            example=ExampleCode(self._get_example_for_pattern(pattern)),
            difficulty=DifficultyLevel.INTERMEDIATE,
            template=TemplatePattern(pattern),
            confidence=ConfidenceScore(0.8)
        )
    
    def _get_example_for_pattern(self, pattern: str) -> str:
        """Get example for a pattern."""
        examples = {
            "$var = $expr": "x = 0",
            "$eq1 && $eq2": "x = 0 && y = 1",
            "{$var}:$type $constraint": "{a}:sbf x = 0",
            "$output[t] = $input[t]": "output[t] = input1[t] & input2[t]"
        }
        return examples.get(pattern, "")