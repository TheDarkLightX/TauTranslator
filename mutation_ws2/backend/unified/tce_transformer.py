"""CanonicalTCETransformer

Maps parse-trees produced by the canonical Tau Controlled English grammar
(`tce_canonical.lark`) into Tau language strings following a strict 1-to-1 mapping
with canonical Tau syntax, as observed in official demo files.

Currently implemented patterns:
    • "X is a Y"  →  Y(X)         (e.g., "socrates is a man." → man(socrates))
    • "X has Y"    →  has(X, Y)   (predicate name appears verbatim in demos)

The transformer will be expanded iteratively with additional constructs, each
validated against real Tau examples.

The transformer can be incrementally extended to cover the full Tau grammar.
"""
from __future__ import annotations

from typing import Any, Dict
from lark import Transformer, Token, Tree

def _format_name(item):
    """Formats a name, handling proper nouns (like 'Socrates') correctly."""
    if isinstance(item, str):
        return item
    if isinstance(item, Token):
        # If the original word was capitalized, keep it that way.
        if item.value[0].isupper():
            return item.value
        return item.value.lower()
    if isinstance(item, Tree):
        # It's a multi-word noun phrase
        words = [t.value for t in item.children]
        # If the first word is capitalized, assume it's a proper name.
        if words[0][0].isupper():
            return "_".join(words)
        return "_".join(w.lower() for w in words)
    return str(item)

def _format_predicate_name(tree):
    """Formats a noun phrase into a snake_case predicate name."""
    return "_".join(t.value.lower() for t in tree.scan_values(lambda v: isinstance(v, Token)))

class TCETransformer(Transformer):
    """Transforms the TCE parse tree into canonical Tau expressions."""

    def WORD(self, token):
        return token

    def ARTICLE(self, token):
        return None # Articles are grammatically necessary but semantically ignored.

    def noun_phrase(self, items):
        # Filter out None from optional articles
        items = [item for item in items if item is not None]
        if len(items) == 1:
            return items[0]
        # This handles multi-word phrases, joining them into a single identifier.
        return _format_predicate_name(Tree('noun_phrase', items))

    def complex_noun_phrase(self, items):
        subject, verb, obj = items
        return Tree('complex_noun_phrase_data', [subject, verb, obj])

    def is_a(self, items):
        return Tree('is_a_pred', items)

    def is_not_a(self, items):
        return Tree('is_not_a_pred', items)

    def relation(self, items):
        return Tree('relation_pred', items)

    def property_verb(self, items):
        return Tree('property_verb_pred', items)

    def simple_fact(self, items):
        subject, predicate_tree = items
        subj_name = _format_name(subject)

        if predicate_tree.data == 'is_a_pred':
            prop_name = _format_predicate_name(predicate_tree.children[0])
            return f"{prop_name}({subj_name}) := true."
        elif predicate_tree.data == 'is_not_a_pred':
            prop_name = _format_predicate_name(predicate_tree.children[0])
            return f"not {prop_name}({subj_name}) := true."
        elif predicate_tree.data == 'relation_pred':
            verb, obj = predicate_tree.children
            verb_name = _format_name(verb)
            obj_name = _format_name(obj)
            return f"{verb_name}({subj_name}, {obj_name}) := true."
        elif predicate_tree.data == 'property_verb_pred':
            prop_name = _format_name(predicate_tree.children[0])
            return f"{prop_name}({subj_name}) := true."

    def logical_and(self, items):
        if len(items) == 1:
            return items[0]
        # This is a bit of a hack to strip the trailing '.' and ' := true'
        # for combination in a logical expression.
        children = [str(i).replace(' := true.', '') for i in items]
        return f"({' and '.join(children)})"

    def logical_or(self, items):
        if len(items) == 1:
            return items[0]
        children = [str(i).replace(' := true.', '') for i in items]
        return f"({' or '.join(children)})"

    def simple_statement(self, items):
        # If it's a logical expression, it needs to be asserted as true.
        expr = items[0]
        if expr.startswith('(') and expr.endswith(')'):
             return f"{expr} := true."
        return expr

    def quantified_statement(self, items):
        quantifier, subject_phrase, predicate = items
        var = 'X' # Use uppercase for variables by convention

        # Handle complex subjects like "student who studies logic"
        if isinstance(subject_phrase, Tree) and subject_phrase.data == 'complex_noun_phrase_data':
            subj_base, verb, obj = subject_phrase.children
            subj_base_name = _format_name(subj_base)
            verb_name = _format_name(verb)
            obj_name = _format_name(obj)
            condition_part1 = f"{subj_base_name}({var})"
            condition_part2 = f"{verb_name}({var}, {obj_name})"
            condition = f"({condition_part1} and {condition_part2})"
        else:
            subj_name = _format_name(subject_phrase)
            condition = f"{subj_name}({var})"

        # Handle the predicate part
        if predicate.data == 'is_a_pred':
            prop_name = _format_predicate_name(predicate.children[0])
            conclusion = f"{prop_name}({var})"
        else:
            # Fallback for other predicate types if needed
            conclusion = "true" # Should be refined

        if quantifier.data == 'universal':
            return f"{conclusion} := {condition}."
        elif quantifier.data == 'existential':
            # Combine the subject and predicate conditions for existential
            full_condition = f"({condition} and {conclusion})"
            return f"exists {var} : {full_condition}."

    def statement(self, items):
        return items[0]

    def fact(self, items):
        return items[0]

    def universal(self, _):
        return Tree('universal', [])

    def existential(self, _):
        return Tree('existential', [])

    def VERB(self, token):
        return token

    def AND(self, _): return "and"
    def OR(self, _): return "or"

    def spec(self, items):
        """Top-level rule, joins multiple statements."""
        return "\n".join(items)

    # ---- default --------------------------------------------------------
    def __default__(self, data, children, meta):
        """Pass through unhandled tokens or trees."""
        if len(children) == 1:
            return children[0]
        return children

# Convenience function -----------------------------------------------------

def transform_tree(tree: Tree) -> str:
    """Transform a parse tree into Tau string using TCETransformer."""
    return TCETransformer().transform(tree)
