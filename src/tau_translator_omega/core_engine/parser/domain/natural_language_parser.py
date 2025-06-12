"""
Natural language parser for true NL to Tau translation following the Intentional Disclosure Principle.

Implements a multi-stage approach: NL → Semantic Parse → CNL → ILR → TCE → Tau

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from returns.result import Result, Success, Failure
from returns.maybe import Maybe, Some, Nothing

from .types import SourceCode, NodeType, ParseNode, ParseTree


@dataclass(frozen=True)
class SemanticFrame:
    """Represents a semantic understanding of a sentence."""
    frame_type: str  # e.g., "universal_quantification", "conditional", "definition"
    participants: Dict[str, Any] = field(default_factory=dict)
    modifiers: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_cnl(self) -> str:
        """Convert semantic frame to controlled natural language."""
        converters = {
            "universal_quantification": self._convert_universal,
            "existential_quantification": self._convert_existential,
            "conditional": self._convert_conditional,
            "definition": self._convert_definition,
            "constraint": self._convert_constraint,
            "temporal": self._convert_temporal
        }
        
        converter = converters.get(self.frame_type)
        if converter:
            return converter()
        
        return ""
    
    def _convert_universal(self) -> str:
        """Convert universal quantification to CNL."""
        var = self.participants.get("variable", "x")
        domain = self.participants.get("domain", "")
        predicate = self.participants.get("predicate", "")
        
        if domain:
            return f"for all {var} in {domain}, {predicate}."
        return f"for all {var}, {predicate}."
    
    def _convert_existential(self) -> str:
        """Convert existential quantification to CNL."""
        var = self.participants.get("variable", "x")
        predicate = self.participants.get("predicate", "")
        
        return f"exists {var} such that {predicate}."
    
    def _convert_conditional(self) -> str:
        """Convert conditional to CNL."""
        condition = self.participants.get("condition", "")
        consequence = self.participants.get("consequence", "")
        
        return f"if {condition} then {consequence}."
    
    def _convert_definition(self) -> str:
        """Convert definition to CNL."""
        name = self.participants.get("name", "")
        params = self.participants.get("parameters", [])
        body = self.participants.get("body", "")
        
        if params:
            param_str = ", ".join(params)
            return f"function {name}({param_str}) returns {body}."
        return f"{name} is {body}."
    
    def _convert_constraint(self) -> str:
        """Convert constraint to CNL."""
        subject = self.participants.get("subject", "")
        constraint = self.participants.get("constraint", "")
        
        return f"{subject} {constraint}."
    
    def _convert_temporal(self) -> str:
        """Convert temporal statement to CNL."""
        temporal_op = self.participants.get("operator", "always")
        predicate = self.participants.get("predicate", "")
        
        return f"{temporal_op} {predicate}."


class DependencyParser:
    """
    Lightweight dependency parser for understanding sentence structure.
    Uses patterns and heuristics rather than full NLP models.
    """
    
    def parse_dependencies(self, sentence: str) -> Result[Dict[str, Any], str]:
        """Parse sentence into dependency structure."""
        tokens = self._tokenize(sentence)
        if not tokens:
            return Failure("Empty sentence")
        
        # Identify main verb and arguments
        verb_idx = self._find_main_verb(tokens)
        if verb_idx < 0:
            return Failure("No main verb found")
        
        # Extract subject, object, modifiers
        subject = self._extract_subject(tokens, verb_idx)
        obj = self._extract_object(tokens, verb_idx)
        modifiers = self._extract_modifiers(tokens, verb_idx)
        
        return Success({
            "tokens": tokens,
            "main_verb": tokens[verb_idx],
            "verb_index": verb_idx,
            "subject": subject,
            "object": obj,
            "modifiers": modifiers
        })
    
    def _tokenize(self, sentence: str) -> List[str]:
        """Simple tokenization."""
        import re
        # Keep contractions together, split on whitespace and punctuation
        tokens = re.findall(r"\w+(?:'\w+)?|[^\w\s]", sentence.lower())
        return tokens
    
    def _find_main_verb(self, tokens: List[str]) -> int:
        """Find main verb using heuristics."""
        # Common verb patterns
        verb_patterns = {
            "be_verbs": ["is", "are", "was", "were", "be", "been", "being"],
            "modal_verbs": ["must", "should", "can", "could", "will", "would", "shall", "may", "might"],
            "action_verbs": ["has", "have", "had", "do", "does", "did", "make", "makes", "exist", "exists"]
        }
        
        # Look for modals first (they indicate the main verb follows)
        for i, token in enumerate(tokens):
            if token in verb_patterns["modal_verbs"]:
                # Main verb likely follows modal
                if i + 1 < len(tokens):
                    return i + 1
        
        # Look for be verbs
        for i, token in enumerate(tokens):
            if token in verb_patterns["be_verbs"]:
                return i
        
        # Look for action verbs
        for i, token in enumerate(tokens):
            if token in verb_patterns["action_verbs"]:
                return i
        
        # Fallback: assume verb is after subject (usually position 1 or 2)
        return min(1, len(tokens) - 1)
    
    def _extract_subject(self, tokens: List[str], verb_idx: int) -> Optional[str]:
        """Extract subject (usually before verb)."""
        if verb_idx > 0:
            # Simple heuristic: subject is the noun phrase before verb
            subject_tokens = tokens[:verb_idx]
            # Filter out determiners
            subject_tokens = [t for t in subject_tokens if t not in ["the", "a", "an", "every", "all", "each"]]
            if subject_tokens:
                return " ".join(subject_tokens)
        return None
    
    def _extract_object(self, tokens: List[str], verb_idx: int) -> Optional[str]:
        """Extract object (usually after verb)."""
        if verb_idx < len(tokens) - 1:
            object_tokens = tokens[verb_idx + 1:]
            # Remove trailing punctuation
            if object_tokens and object_tokens[-1] in [".", "!", "?"]:
                object_tokens = object_tokens[:-1]
            if object_tokens:
                return " ".join(object_tokens)
        return None
    
    def _extract_modifiers(self, tokens: List[str], verb_idx: int) -> List[str]:
        """Extract modifiers and qualifiers."""
        modifiers = []
        
        # Check for negation
        if verb_idx > 0 and tokens[verb_idx - 1] in ["not", "no", "never"]:
            modifiers.append("negation")
        
        # Check for quantifiers
        quantifiers = ["all", "every", "some", "any", "each", "no"]
        for token in tokens[:verb_idx]:
            if token in quantifiers:
                modifiers.append(f"quantifier:{token}")
        
        return modifiers


class SemanticAnalyzer:
    """
    Analyzes sentence meaning and maps to logical structures.
    This is the key component that bridges NL to formal logic.
    """
    
    def __init__(self):
        """Initialize semantic analyzer."""
        self._frame_patterns = self._initialize_frame_patterns()
        self._concept_mappings = self._initialize_concept_mappings()
    
    def analyze_semantics(self, dependencies: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Analyze dependencies to extract semantic meaning."""
        # Try each frame pattern
        for frame_type, pattern_checker in self._frame_patterns.items():
            if pattern_checker(dependencies):
                frame_result = self._build_semantic_frame(frame_type, dependencies)
                if isinstance(frame_result, Success):
                    return frame_result
        
        return Failure("No matching semantic frame found")
    
    def _initialize_frame_patterns(self) -> Dict[str, Any]:
        """Initialize patterns for semantic frame detection."""
        return {
            "universal_quantification": self._is_universal_quantification,
            "existential_quantification": self._is_existential_quantification,
            "conditional": self._is_conditional,
            "definition": self._is_definition,
            "constraint": self._is_constraint,
            "temporal": self._is_temporal
        }
    
    def _initialize_concept_mappings(self) -> Dict[str, str]:
        """Initialize mappings from NL concepts to formal concepts."""
        return {
            # Quantifiers
            "all": "for all",
            "every": "for all",
            "each": "for all",
            "any": "for all",
            "some": "exists",
            "there is": "exists",
            "there are": "exists",
            
            # Logical operators
            "and": "and",
            "or": "or",
            "not": "not",
            "if": "if",
            "then": "then",
            "implies": "implies",
            "whenever": "if",
            "when": "if",
            
            # Comparisons
            "greater than": ">",
            "less than": "<",
            "equal to": "=",
            "equals": "=",
            "is": "=",
            
            # Temporal
            "always": "always",
            "never": "not always",
            "sometimes": "sometimes",
            "eventually": "eventually"
        }
    
    def _is_universal_quantification(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence expresses universal quantification."""
        tokens = deps.get("tokens", [])
        modifiers = deps.get("modifiers", [])
        
        # Check for universal quantifiers
        universal_keywords = ["all", "every", "each", "any"]
        has_universal = any(
            keyword in tokens or f"quantifier:{keyword}" in modifiers
            for keyword in universal_keywords
        )
        
        # Check for patterns like "X are Y" (implicit universal)
        verb = deps.get("main_verb", "")
        if verb in ["are", "have", "must"] and deps.get("subject", "").endswith("s"):
            has_universal = True
        
        return has_universal
    
    def _is_existential_quantification(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence expresses existential quantification."""
        tokens = deps.get("tokens", [])
        
        existential_patterns = [
            ["there", "is"],
            ["there", "are"],
            ["there", "exists"],
            ["some"],
            ["at", "least", "one"]
        ]
        
        for pattern in existential_patterns:
            if all(word in tokens for word in pattern):
                return True
        
        return False
    
    def _is_conditional(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence expresses conditional."""
        tokens = deps.get("tokens", [])
        
        conditional_keywords = ["if", "when", "whenever", "unless"]
        return any(keyword in tokens for keyword in conditional_keywords)
    
    def _is_definition(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence is a definition."""
        verb = deps.get("main_verb", "")
        tokens = deps.get("tokens", [])
        
        # Patterns: "X is defined as Y", "X means Y", "Let X be Y"
        definition_verbs = ["is", "means", "equals", "denotes"]
        definition_markers = ["defined", "definition", "let", "means"]
        
        return (verb in definition_verbs and 
                any(marker in tokens for marker in definition_markers))
    
    def _is_constraint(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence expresses a constraint."""
        verb = deps.get("main_verb", "")
        
        # Simple constraints use "is", "must", "should" with comparisons
        constraint_verbs = ["is", "are", "must", "should", "has", "have"]
        return verb in constraint_verbs and not self._is_definition(deps)
    
    def _is_temporal(self, deps: Dict[str, Any]) -> bool:
        """Check if sentence has temporal operators."""
        tokens = deps.get("tokens", [])
        
        temporal_keywords = ["always", "never", "sometimes", "eventually", "until"]
        return any(keyword in tokens for keyword in temporal_keywords)
    
    def _build_semantic_frame(
        self,
        frame_type: str,
        deps: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Build semantic frame from dependencies."""
        builders = {
            "universal_quantification": self._build_universal_frame,
            "existential_quantification": self._build_existential_frame,
            "conditional": self._build_conditional_frame,
            "definition": self._build_definition_frame,
            "constraint": self._build_constraint_frame,
            "temporal": self._build_temporal_frame
        }
        
        builder = builders.get(frame_type)
        if builder:
            return builder(deps)
        
        return Failure(f"No builder for frame type: {frame_type}")
    
    def _build_universal_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build universal quantification frame."""
        subject = deps.get("subject", "x")
        predicate = deps.get("object", "")
        
        # Extract variable from subject
        # "all numbers" -> variable: "number", domain: "numbers"
        if subject.startswith("all "):
            variable = subject[4:].rstrip("s")  # Simple pluralization
        elif subject.startswith("every "):
            variable = subject[6:]
        else:
            variable = "x"
        
        return Success(SemanticFrame(
            frame_type="universal_quantification",
            participants={
                "variable": variable,
                "predicate": predicate or f"{variable} exists"
            }
        ))
    
    def _build_existential_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build existential quantification frame."""
        obj = deps.get("object", "")
        
        # Extract what exists
        if obj.startswith("a ") or obj.startswith("an "):
            variable = obj.split()[1]
        else:
            variable = obj or "x"
        
        return Success(SemanticFrame(
            frame_type="existential_quantification",
            participants={
                "variable": variable,
                "predicate": f"{variable} exists"
            }
        ))
    
    def _build_conditional_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build conditional frame."""
        tokens = deps["tokens"]
        
        # Find if/then structure
        if_idx = tokens.index("if") if "if" in tokens else -1
        then_idx = tokens.index("then") if "then" in tokens else -1
        
        if if_idx >= 0:
            if then_idx > if_idx:
                condition = " ".join(tokens[if_idx + 1:then_idx])
                consequence = " ".join(tokens[then_idx + 1:])
            else:
                # Implicit then after comma
                condition_end = len(tokens)
                for i in range(if_idx + 1, len(tokens)):
                    if tokens[i] in [",", "then"]:
                        condition_end = i
                        break
                
                condition = " ".join(tokens[if_idx + 1:condition_end])
                consequence = " ".join(tokens[condition_end + 1:])
            
            return Success(SemanticFrame(
                frame_type="conditional",
                participants={
                    "condition": condition.strip(" ,"),
                    "consequence": consequence.strip(" .")
                }
            ))
        
        return Failure("Could not parse conditional structure")
    
    def _build_definition_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build definition frame."""
        subject = deps.get("subject", "")
        obj = deps.get("object", "")
        
        return Success(SemanticFrame(
            frame_type="definition",
            participants={
                "name": subject,
                "body": obj
            }
        ))
    
    def _build_constraint_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build constraint frame."""
        subject = deps.get("subject", "")
        verb = deps.get("main_verb", "")
        obj = deps.get("object", "")
        
        # Construct constraint expression
        if verb in ["is", "are"]:
            constraint = obj
        else:
            constraint = f"{verb} {obj}"
        
        return Success(SemanticFrame(
            frame_type="constraint",
            participants={
                "subject": subject,
                "constraint": constraint
            }
        ))
    
    def _build_temporal_frame(self, deps: Dict[str, Any]) -> Result[SemanticFrame, str]:
        """Build temporal frame."""
        tokens = deps["tokens"]
        
        # Find temporal operator
        temporal_ops = ["always", "never", "sometimes", "eventually"]
        operator = None
        op_idx = -1
        
        for op in temporal_ops:
            if op in tokens:
                operator = op
                op_idx = tokens.index(op)
                break
        
        if operator:
            # Everything after operator is the predicate
            predicate = " ".join(tokens[op_idx + 1:])
            
            return Success(SemanticFrame(
                frame_type="temporal",
                participants={
                    "operator": operator,
                    "predicate": predicate.strip(" .")
                }
            ))
        
        return Failure("No temporal operator found")


class NaturalLanguageParser:
    """
    Main parser that orchestrates NL → CNL → ILR pipeline.
    This is the entry point for true natural language parsing.
    """
    
    def __init__(self):
        """Initialize natural language parser."""
        self._dependency_parser = DependencyParser()
        self._semantic_analyzer = SemanticAnalyzer()
        self._ambiguity_resolver = AmbiguityResolver()
    
    async def parse_natural_language_async(self, text: str) -> Result[List[str], str]:
        """
        Parse natural language text into CNL statements.
        Returns list of CNL statements ready for ILR translation.
        """
        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return Failure("No sentences found in input")
        
        cnl_statements = []
        errors = []
        
        for sentence in sentences:
            result = await self._parse_single_sentence_async(sentence)
            if isinstance(result, Success):
                cnl_statements.append(result.unwrap())
            else:
                errors.append(f"Failed to parse: '{sentence}' - {result.failure()}")
        
        if cnl_statements:
            return Success(cnl_statements)
        else:
            return Failure("\n".join(errors))
    
    async def _parse_single_sentence_async(self, sentence: str) -> Result[str, str]:
        """Parse single sentence to CNL."""
        # Parse dependencies
        deps_result = self._dependency_parser.parse_dependencies(sentence)
        if isinstance(deps_result, Failure):
            return deps_result
        
        deps = deps_result.unwrap()
        
        # Analyze semantics
        semantic_result = self._semantic_analyzer.analyze_semantics(deps)
        if isinstance(semantic_result, Failure):
            # Try ambiguity resolution
            resolved = self._ambiguity_resolver.resolve_ambiguity(sentence, deps)
            if isinstance(resolved, Success):
                semantic_result = resolved
            else:
                return semantic_result
        
        frame = semantic_result.unwrap()
        
        # Convert to CNL
        cnl = frame.to_cnl()
        if not cnl:
            return Failure(f"Could not convert frame to CNL: {frame.frame_type}")
        
        return Success(cnl)
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        
        # Simple sentence splitting on . ! ?
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences


class AmbiguityResolver:
    """
    Resolves ambiguities in natural language using context and heuristics.
    This is crucial for handling real-world language variations.
    """
    
    def resolve_ambiguity(
        self,
        sentence: str,
        dependencies: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Try to resolve ambiguous sentences."""
        # Common ambiguity patterns
        patterns = [
            self._resolve_implicit_quantification,
            self._resolve_pronoun_reference,
            self._resolve_comparison_direction,
            self._resolve_missing_verb
        ]
        
        for resolver in patterns:
            result = resolver(sentence, dependencies)
            if isinstance(result, Success):
                return result
        
        return Failure("Could not resolve ambiguity")
    
    def _resolve_implicit_quantification(
        self,
        sentence: str,
        deps: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Resolve implicit universal quantification."""
        # "Numbers greater than zero are positive" → "for all x > 0, x is positive"
        
        subject = deps.get("subject", "")
        if subject and subject.endswith("s"):  # Plural
            # Likely universal quantification
            singular = subject.rstrip("s")
            predicate = deps.get("object", "")
            
            return Success(SemanticFrame(
                frame_type="universal_quantification",
                participants={
                    "variable": singular,
                    "predicate": predicate
                },
                confidence=0.8  # Lower confidence for implicit
            ))
        
        return Failure("Not implicit quantification")
    
    def _resolve_pronoun_reference(
        self,
        sentence: str,
        deps: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Resolve pronoun references."""
        # For now, simple replacement of "it" with last noun
        # In real system, would track discourse context
        
        tokens = deps.get("tokens", [])
        if "it" in tokens:
            # Find last noun before "it"
            it_idx = tokens.index("it")
            
            # Common nouns in math/logic context
            candidate_nouns = ["number", "value", "variable", "expression", "set"]
            
            for i in range(it_idx - 1, -1, -1):
                if tokens[i] in candidate_nouns:
                    # Replace "it" with the noun
                    new_tokens = tokens.copy()
                    new_tokens[it_idx] = tokens[i]
                    
                    # Re-analyze with resolved reference
                    new_deps = deps.copy()
                    new_deps["tokens"] = new_tokens
                    
                    analyzer = SemanticAnalyzer()
                    return analyzer.analyze_semantics(new_deps)
        
        return Failure("No pronoun to resolve")
    
    def _resolve_comparison_direction(
        self,
        sentence: str,
        deps: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Resolve ambiguous comparisons."""
        # "x is larger than y" → "x > y"
        
        comparison_mappings = {
            "larger": ">",
            "bigger": ">",
            "greater": ">",
            "smaller": "<",
            "less": "<",
            "equal": "="
        }
        
        tokens = deps.get("tokens", [])
        for word, op in comparison_mappings.items():
            if word in tokens:
                # Build comparison constraint
                idx = tokens.index(word)
                
                # Find compared items
                left = " ".join(tokens[:idx])
                right = " ".join(tokens[idx + 2:]) if idx + 2 < len(tokens) else ""
                
                return Success(SemanticFrame(
                    frame_type="constraint",
                    participants={
                        "subject": left,
                        "constraint": f"{op} {right}"
                    }
                ))
        
        return Failure("No comparison found")
    
    def _resolve_missing_verb(
        self,
        sentence: str,
        deps: Dict[str, Any]
    ) -> Result[SemanticFrame, str]:
        """Handle sentences with implicit verbs."""
        # "All positive numbers" → "All positive numbers exist"
        
        verb = deps.get("main_verb", "")
        if not verb or verb == "":
            # Add implicit "exists" or "is true"
            subject = deps.get("subject", "")
            
            return Success(SemanticFrame(
                frame_type="constraint",
                participants={
                    "subject": subject,
                    "constraint": "exists"
                },
                confidence=0.7
            ))
        
        return Failure("Verb present")